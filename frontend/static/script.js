const animationFramesStatic = [
    'assets/girl-47.jpg',
    'assets/girl-48.jpg',
    'assets/girl-51.jpg'
];

const animationFramesActive = [
    'assets/girl-30.jpg',
    'assets/girl-31.jpg',
    'assets/girl-32.jpg',
    'assets/girl-33.jpg'
];

let currentFrameIndex = 0;
let currentAnimation = animationFramesStatic;
let animationInterval;
let mediaRecorder;
let recordedChunks = [];

function setAnimation(isActive) {
    clearInterval(animationInterval);
    
    currentAnimation = isActive ? animationFramesActive : animationFramesStatic;
    
    animationInterval = setInterval(() => {
        document.getElementById('animation').style.backgroundImage = `url(${currentAnimation[currentFrameIndex]})`;
        currentFrameIndex = (currentFrameIndex + 1) % currentAnimation.length;
    }, 500);
}

setAnimation(false);

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
            console.log("Size of the audio blob:", audioBlob.size);
            sendAudioToBackend(audioBlob);
            recordedChunks = [];  // Clear the recorded chunks for the next recording
        };
    })
    .catch(err => {
        console.error('Error accessing microphone:', err);
    });

document.getElementById('startRecording').addEventListener('click', function() {
    if (mediaRecorder) {
        mediaRecorder.start();
        updateStatus("Recording...");
    }
});

document.getElementById('stopRecording').addEventListener('click', function() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        updateStatus("I'm thinking...");
    }
});

function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    fetch('/transcribe_and_respond', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Audio URL:', data.audio_url);
        const statusMessage = "Transcription: " + data.transcription + "\nResponse: " + data.response;
        updateStatus(statusMessage);  // First update the status

        // Then play the returned audio and set the animation to active
        const responseAudio = new Audio(data.audio_url);
        
        responseAudio.onplay = function() {
            setAnimation(true);  // Start the active animation when the audio starts playing
        };

        responseAudio.onended = function() {
            setAnimation(false);  // Reset to static animation after audio is finished
        };
        
        // Load and play the audio data
        responseAudio.load();
        responseAudio.play();
    })
    .catch(error => {
        console.error('Error sending audio data:', error);
    });
}

function updateStatus(message) {
    document.getElementById('statusWindow').innerText = message;
}
