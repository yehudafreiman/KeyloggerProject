from flask import Flask, request
app = Flask(__name__)
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('received.encrypted')
    return 'OK', 200
app.run(port=5000)