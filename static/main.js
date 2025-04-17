
const fileInput = document.getElementById("fileInput");
const uploadBtn  = document.getElementById("uploadBtn");
const recordBtn  = document.getElementById("recordBtn");
const stopBtn    = document.getElementById("stopBtn");



const streamStart = document.getElementById("streamStart");
const streamStop  = document.getElementById("streamStop");

const statusDiv = document.getElementById("status");
const resultDiv = document.getElementById("result");

function chosenLang() {
  return document.querySelector('input[name="lang"]:checked').value;
}

//upload fichier
uploadBtn.onclick = async () => {
  if (!fileInput.files.length) return alert("Choisissez un fichier");
  await sendFile(fileInput.files[0]);
};

//enregistrement POST nornal
let recorder, chunks=[];
recordBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = e => chunks.push(e.data);
  recorder.start();
  recordBtn.disabled = true; stopBtn.disabled = false;
  statusDiv.textContent = "Enregistrement…";
};
stopBtn.onclick = () => {
  recorder.stop();
  recorder.onstop = () => {
    const blob = new Blob(chunks, {type: recorder.mimeType});
    chunks=[];
    recordBtn.disabled=false; stopBtn.disabled=true;
    statusDiv.textContent="Transcription…";
    sendFile(new File([blob], "mic.webm",{type:blob.type}));
  };
};

//streaming WebS
let ws, streamRecorder;
streamStart.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});
  streamRecorder = new MediaRecorder(stream, {audioBitsPerSecond:128000});
  ws = new WebSocket(`ws://${location.host}/ws/stream?lang=${chosenLang()}`);

  ws.onmessage = e => { resultDiv.textContent += e.data; };
  ws.onopen = () => {
    streamRecorder.ondataavailable = ev => ws.send(ev.data);
    // chunk toutes les 500 ms
    streamRecorder.start(500); 
    streamStart.disabled = true; streamStop.disabled = false;
    statusDiv.textContent = "Streaming…";
  };
};
streamStop.onclick = () => {
  streamRecorder.stop();
  ws.close();
  streamStart.disabled = false; streamStop.disabled = true;
  statusDiv.textContent = "";
};
//helper
async function sendFile(file){
  statusDiv.textContent = "Envoi…"; resultDiv.textContent="";
  const form = new FormData(); form.append("audio", file);
  const r = await fetch(`/transcription?lang=${chosenLang()}`,{method:"POST",body:form});
  const data = await r.json();
  resultDiv.textContent = r.ok ? data.text : `Erreur ${r.status}: ${data.detail}`;
  statusDiv.textContent="";
}
