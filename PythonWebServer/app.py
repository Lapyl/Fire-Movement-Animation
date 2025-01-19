from flask import Flask, render_template, request, abort
import requests
import urllib.parse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import MultipleLocator
from IPython.display import HTML

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 96 * 1024 * 1024  # 96 MB

@app.route('/')
def init():
    return render_template('tools.html')

@app.route('/fma')
def fma():
    return render_template('fma.html')

@app.route('/fmares', methods=['POST'])
def fmares():
    if request.method == 'POST':
        xlat = request.form['Latitude']
        xlon = request.form['Longitude']
        xadr = request.form['Address']
        xcit = request.form['City']
        xcon = request.form['Country']
        xsec = request.form['Seconds']
        print('(a) ' + xlat + ' ' + xlon + ' ' + xadr + ' ' + xcit + ' ' + xcon + ' ' + xsec)
        zres = ''
        if (len(xadr)>1) and (len(xcit)>1) and (len(xcon)>1):
            zres = requests.get('https://nominatim.openstreetmap.org/search?q=' +
                                urllib.parse.quote(xadr + ', ' + xcit + ', ' + xcon) + '&format=json').text
            print('(b) ' + zres)
        zlat = ''
        if len(zres)>1:
            try:
                zlat = zres.json()[0]["lat"]
                print('(c) Latitude ' + str(zlat))
            except:
                print('(d) Latitude could not be computed from the given Address.')
        if len(zlat)<3:
            if len(xlat)>1:
                zlat = float(xlat)
                print('(e) Latitude ' + str(zlat))
        if len(str(zlat))<3:
            zlat = 19.4
            print('(f) Latitude ' + str(zlat))
        zlon = ''
        if (len(zres)>1):
            try:
                zlon = zres.json()[0]["lon"]
                print('(g) Longitude ' + str(zlon))
            except:
                print('(h) Longitude could not be computed from the given Address.')
        if len(zlon)<3:
            if len(xlon)>1:
                zlon = float(xlon)
                print('(i) Longitude ' + str(zlon))
        if len(str(zlon))<3:
            zlon = -155.29
            print('(j) Longitude ' + str(zlon))
        zsec = 1
        if len(xsec)>0:
            zsec = float(xsec)
            print('(k) Seconds ' + str(zsec))
        print('(l) ' + str(zlat) + ' ' + str(zlon) + ' ' + str(zsec))
        zcsv = pd.read_csv('ref/Fires.csv')
        zcsv = zcsv[(zcsv['latitude']>zlat-0.011) & (zcsv['latitude']<zlat+0.011) & (zcsv['longitude']>zlon-0.011) & (zcsv['longitude']<zlon+0.011)]
        zcsv.sort_values(by='datetime', axis=0, ascending=True, inplace=True)
        zdts = zcsv.datetime.unique()
        zcsv.sort_values(by='latitude', axis=0, ascending=True, inplace=True)
        zlas = zcsv.latitude.unique()
        zcsv.sort_values(by='longitude', axis=0, ascending=True, inplace=True)
        zlos = zcsv.longitude.unique()
        zrec=len(zdts)
        zhtm="<h2>No fires around the specified location<h2>"
        if zrec>0:
            fig, ax = plt.subplots()
            dot, = ax.plot([], [], 'rs')
            plt.title('Fires around longitude ' + str(zlon) + ' latitude ' + str(zlat))
            plt.text(0.5, 0.5, 'X', fontsize=8, transform=ax.transAxes)
            ztxt = plt.text(0.1, 0.1, 'x', fontsize=20, transform=ax.transAxes)
            plt.xticks(fontsize=6, rotation=90)
            ax.xaxis.set_major_locator(MultipleLocator(0.001))
            plt.yticks(fontsize=6)
            ax.yaxis.set_major_locator(MultipleLocator(0.001))
            def init():
                ax.set_xlim(zlos[0]-0.001, zlos[-1]+0.001)
                ax.set_ylim(zlas[0]-0.001, zlas[-1]+0.001)
                return dot,
            def update(i):
                ztxt.set_text(str(zdts[i]))
                dot.set_data(zcsv[zcsv['datetime']==zdts[i]][['longitude']], zcsv[zcsv['datetime']==zdts[i]][['latitude']])
                dot.set_markersize(10)
                return dot,
            zrec=min(len(zdts),len(zlas),len(zlos))
            zhtm='<h2>No fires around the specified location</h2>'
            animloc = animation.FuncAnimation(fig, update, frames=range(zrec), interval=1000*zsec, init_func=init, blit=True)
            # animloc.save('out/animloc.gif', writer='Pillow', fps=60)
            zhtm = HTML(animloc.to_jshtml())
        return render_template('fmares.html', zlat=zlat, zlon=zlon, zhtm=zhtm)

if __name__ == '__main__':
    app.run()
