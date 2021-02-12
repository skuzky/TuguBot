import difflib, re
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
app =Flask(__name__, template_folder='templates')

@app.route("/")
def home():	
	return render_template("home.html")

@app.route("/_get_data/<tanya>", methods=['POST'])
def _get_data(tanya):
    factory  = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    # text = "Jam Buka Gembiraloka adalah 08 - 5 sore . Jam Buka Malioboro yaitu dari jam 9 - 10 .Lokasi Malioboro berada di Jalan Malioboro, Sosrorumedan .  Biaya tiket masuk malioboro adalah 15 ribu"
    with open('db/resonse.txt','r') as file:
        dataresp = file.read()
 
    with open("db/katadasar.txt", "r") as f:
        contents = f.read().splitlines()

    with open("db/daftar_kota.txt", "r") as f:
        kota = f.read().splitlines()

    suggestion = []
    list_wisata = ['situs warungboto']

    # define db teks
    text = dataresp
    txt_lower = text.lower()
    # define pattern
    pertanyaan = tanya.lower()


    # perubahan pola
    if 'alamat' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('alamat', 'lokasi')
    elif 'waktu operasional' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('waktu operasional', 'jam buka')
    elif 'jam operasional' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('jam operasional', 'jam buka')
    elif 'waktu' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('waktu','jam')
    elif 'berapa biaya tiket masuk' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('berapa biaya tiket masuk', 'harga tiket')
    elif 'berapa biaya' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('berapa biaya', 'harga')
    elif 'jam berapa museum' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('jam berapa museum', 'museum')
    elif 'jam berapa' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('jam berapa', '')
    elif 'masuk' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('masuk', '')
    elif 'letak' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('letak', 'lokasi')
    elif 'berapa' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('berapa','')
    elif 'kapan' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('kapan', '')
    elif 'biaya' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('biaya', 'harga')
    elif 'titik 0 kilometer' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('0', 'nol')
    elif 'titik 0 km' in pertanyaan:
        new_pertanyaan = pertanyaan.replace('0 km', 'nol kilometer')
    elif 'lokasi malioboro':
        new_pertanyaan = pertanyaan.replace('lokasi malioboro', 'lokasi jalan malioboro')
    else:
        new_pertanyaan = pertanyaan

    stop_pattern = stopword.remove(new_pertanyaan)
    new_pattern  = stop_pattern

    for kata in new_pattern.casefold().split():
        if kata not in contents:
            suggestion = difflib.get_close_matches(kata, contents)

    if not suggestion:
        result = BMSearch(txt_lower,new_pattern)
        kotas = ["kebun plasma nuftah","situs warungboto","museum vredeburg","jalan malioboro","de mata museum","masjid gedhe kauman","tugu jogja","museum sonobudoyo","plengkung gading","museum bahari","alun alun kidul","alun alun utara","taman pelangi","taman pintar","titik nol kilometer","monumen jogja kembali","museum kereta keraton","taman sari","monumen serangan umum 1 maret","museum sasmitaloka","museum dewantara kirti griya","museum sasana wiratama","gembiraloka"]
        question = ["dimana","berapa","harga","deskripsi","dimana lokasi","berapa harga","berapa harga tiket","kapan","jam buka","jam berapa"]
        belum_ada = ["fasilitas", "sejarah", "video profil"]
        if any(new_pattern in kotas[x] for x in range(len(kotas))):
            new_text = "Silahkan gunakan pertanyaan yang lebih lengkap :)"
        elif any(new_pattern in question[x] for x in range(len(question))):
            new_text = "Mungkin kamu harus memberikan pertanyaan yang lebih lengkap"
        elif (result == -1) or (len(new_pattern) < 5):
            new_text = "Mohon maaf aku tidak mengerti maksud kamu :("
            if(new_pattern in belum_ada[x] for x in range(len(belum_ada))):            
                slit = new_pattern.split(' ')
                for x in range(len(slit)):
                    for a in range(len(belum_ada)):
                        if (belum_ada[a] == slit[x]):
                            gaada =  slit[x]
                            new_text = "Info tentang {} belum terdaftar di dalam database".format(gaada)
            else:
                new_text = "Mohon maaf saku tidak mengerti maksud kamu :("
        else:
            if not new_pattern == None: 
                new_text = [i for i in text.split('.') if new_pattern in i.lower()][0]
                if 'deskripsi' in new_text:
                    new_text = new_text.replace('deskripsi','')
            # new_text = "Mohon maaf aku tidak mengerti maksud kamu :("
            # print(new_text)

        # return render_template("home.html", pertanyaan=new_text)
        return jsonify({'data': render_template('response.html', jawaban=new_text, pertanyaan=pertanyaan, apa=tanya)})
    else:
        # for kata in new_pattern.casefold().split():   
        #     # new_text = f'mungkin maksud anda {", ".join(str(x) for x in suggestion)}'
        #     new_text = f'mungkin maksud anda {", ".join(str(x) for x in suggestion)} ?'
        
        # del suggestion [:]
        return jsonify({'data': render_template('response.html', jawaban=new_text)})

def generateBadCharShift(term):
    skipList = {}
    for i in range(0, len(term)-1):
        skipList[term[i]] = len(term)-i-1
    return skipList


# Actual Search Algorithm
def BMSearch(haystack, needle):
    # goodSuffix = generateSuffixShift(needle)
    badChar = generateBadCharShift(needle)
    i = 0
    while i < len(haystack)-len(needle)+1:
        j = len(needle)
        while j > 0 and needle[j-1] == haystack[i+j-1]:
            j -= 1
        if j > 0:
            badCharShift = badChar.get(haystack[i+j-1], len(needle))
            i += badCharShift
        else:
            return i
    return -1

@app.route("/admin")
def admin():
	return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
            # return redirect(url_for('admin'))
        else:
           return render_template('admin.php', error=error)
    else:
        return render_template('admin.php')
           
@app.route('/tambah_data')
def home_tambah(): 
    file_bio = open("db/resonse.txt", "r")
    data = file_bio.readlines()
    for line in data:
        l = line.split('.')
        var = l
    return render_template('tambah_data.html', var=var)

@app.route('/lihat_data')
def lihat_data():
    opt_param = request.args.get('success')
    if opt_param is None:
        success = ''
    else:   
        success = request.args['success']
    # success = session['success']
    
    file_bio = open("db/resonse.txt", "r")
    data = file_bio.readlines()
    for line in data:
        l = line.split('.')
        var = l
    return render_template('lihat_data.html', var=var, success = success)

@app.route('/proses_tambah_data', methods=['GET','POST'])
def tambah():
    db_file = open('db/resonse.txt', 'a')
    new_teks = request.form['teks_baru']
    # new_var = request.form['var'] 
    write_db = "{} . ".format(new_teks)
    db_file.write(write_db)
    db_file.close()
    success="Aturan baru telah ditambahkan kedalam database"
    # session['success'] = success
    # return render_template('tambah_data.html', success=success)
    return redirect(url_for('lihat_data', success=success))

@app.route('/hapus_data/<id_tanya>')
def hapus(id_tanya):

    db_file = open('db/resonse.txt','r')
    data = db_file.readlines()
    output = []
    for line in  data:
        for line in data:
            if id_tanya in line:
                # line.remove(id_tanya);
                # new = line.replace(id_tanya,'')
                tanya_baru = "{} .".format(id_tanya)
                new = line.replace(tanya_baru,'')
        output.append(new)
    
    db_file.close()
    f = open('db/resonse.txt','w')
    for line in output:
        f.write(line)
    f.close()

    coba = id_tanya
    return redirect(url_for('lihat_data'))

@app.route('/update/<id_tanya>')
def updt(id_tanya):
    get_tanya = id_tanya
    return render_template('update.html', data=get_tanya)

@app.route('/proses_update_data', methods=['GET','POST'])
def update():
    id_tanya = request.form['id_tanya']
    input_baru = request.form['update_aturan']
    db_file = open('db/resonse.txt','r')
    data = db_file.readlines()
    output = []
    for line in  data:
        for line in data:
            if id_tanya in line:
                # line.remove(id_tanya);
                # new = line.replace(id_tanya,'')
                tanya_baru = " {} ".format(input_baru)
                new = line.replace(id_tanya, tanya_baru)
        
        output.append(new)
    
    db_file.close()
    f = open('db/resonse.txt','w')
    for line in output:
        f.write(line)
    f.close()

    coba = id_tanya
    return redirect(url_for('lihat_data'))


if __name__ == "__main__":
    app.run(debug=True)