const Camera=document.getElementById("getStart")
const Asana=document.getElementById("postures")
const posture=document.querySelector(".postures")
const C=document.getElementById("C")
const video = document.getElementById('video');
const arrow=document.getElementById('arrow');
const Desciption=document.getElementById('Description');
const arrow1=document.getElementById('arrow1');
// const asanass=document.getElementById("Asanass")
const img1=document.getElementById('processedImage')
const csrf_token = document.querySelector("input[name='csrfmiddlewaretoken']").value; // Retrieve CSRF token
// let webcamWindow;
// const startButton = document.getElementById('getStart');
function showDescription(divId) {
    // Hide all descriptions and reset opacity
    for (let i = 1; i <= 5; i++) {
        const description = document.getElementById('description' + i);
        const clickableDiv = document.querySelector('.clickable-div');

        description.style.display = 'none';
        clickableDiv.style.opacity = 1;
    }

    // Show the selected description
    const selectedDescription = document.getElementById('description' + divId.substr(-1));
    // const selectedDiv = document.getElementById('div' + divId.substr(-1));
    selectedDescription.style.display = 'block';
    // selectedDiv.style.opacity = 1;
    

    // Reduce the opacity of the other divs
    const otherClickableDivs = document.querySelectorAll('.clickable-div:not([onclick*="' + divId + '"])');
    otherClickableDivs.forEach(function (div) {
        div.style.opacity = 0.5;
        
    });
}
Asana.addEventListener('click', (e)=>{
    console.log(e.target.value);
})
Asana.addEventListener('click', ()=>{
    
    C.style.opacity = '0';
    C.style.maxHeight = '0';
    arrow.style.opacity = '0';
    arrow.style.maxHeight = '0';


    // setTimeout(() => {
    //     C.style.display="None";
    //     arrow.style.display="None";
    // }, 500);
    setTimeout(() => {
        Desciption.style.display="block";
        arrow1.style.display="block";
        posture.style.marginLeft='0';
    }, 500);
    

})
// if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
//     Camera.addEventListener('click', function() {
//         // Request access to the camera
//         navigator.mediaDevices.getUserMedia({ video: true })
//         .then(function (stream) {
//             // Assign the camera stream to the video element
//             video.srcObject = stream;
//         })
//         .catch(function (error) {
//             console.error('Error accessing camera:', error);
//         });
//     });
// } else {
//     console.error('getUserMedia is not supported in this browser');
// }
let isStreaming = false;

Camera.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    isStreaming = true;
    captureAndSendFrames(); // Start frame capturing when the webcam is active
});

async function captureAndSendFrames() {
    const interval = 1000; // Adjust the frame capture rate
    while (isStreaming) {
        await new Promise(resolve => setTimeout(resolve, interval));

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frameData = canvas.toDataURL('image/jpeg');

        // Send frame data to the server asynchronously
        fetch('/capture_frame/', {
            method: 'POST',
            body: JSON.stringify({ frame_data: frameData }),  // Send frame data as JSON
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,  // Include the CSRF token
            },
        }).then(response => response.json())
        .then(data => {
            const processedFrameData = data.processed_frame_data;

            // Assuming you have an <img> element with id 'processedImage'
            const imgElement = document.getElementById('processedImage');
            imgElement.src = `data:image/jpeg;base64,${processedFrameData}`;
            imgElement.style.display = 'block'; // Show the processed image
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    }
}