import React from 'react';
import SpinningProgressBar from './ProgressBar';
import { useRequestContext } from '../RequestContext';
import { useAnalysedData } from '../AnalysedDataContext';

function AnalyseButton() {

    const { request, updateRequest } = useRequestContext();
    const { data, updateAnalysedData } = useAnalysedData();

    const handleClick = async () => {

        if (request.payload.images[request.payload.images.length - 1 ]=== null) {
            return  alert('Please upload an image first.');
        }

        updateRequest({ state: "LOADING" });
        console.log('Request:', request);
    
        const url = 'http://127.0.0.1:5000/predict';
    
        // Encode images to Base64 and prepare payload
        // Hacky way to avoid doing batches, just take the last image with the slice

        let imagesToBase64Promises = request.payload.images.slice(-1).map(file => 
            new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            })
        );

        
        try {
            const base64Images = await Promise.all(imagesToBase64Promises);
            const payloadData = { 
                ...request.payload,
                images: base64Images, // Correctly include base64 images in payload
                model_id: request.payload.model_id,
            };
    
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payloadData),
            });

            console.log('Response:', response);
            
            const response_json = await response.json();
            console.log('RESPONSE OK: 200');
            console.log(response_json);
    
            // Assuming response processing remains the same
            const modelResponse = {
                width: response_json.width,
                height: response_json.height,
                annotations: response_json.annotations,
                composite_masks: response_json.composite_masks,
                seed_indices: response_json.seed_indices,
            };
    
            // Update UI based on response
            updateAnalysedData({
                ...data,
                response: modelResponse,
                state: "COMPLETE",
                batch_id: request.payload.images[0].name.split(".")[0],
                root_image: base64Images[0],
                img: base64Images[0],
            });
    
            updateRequest({ state: "COMPLETE" });
            
        } catch (error) {
            console.error('Error fetching data:', error);
            updateRequest({ state: "ERROR" });
        }
    };
    
    
    
    return (
        <button
        type="button"
        onClick={handleClick}
        disabled={request.payload.images.length < 1}
        className={`flex w-full items-center mt-4 justify-center gap-x-2 rounded-md px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 ${request.state === "LOADING" ? 'bg-indigo-800' : 'bg-indigo-600'}`}
        >
            {request.state === "LOADING" ? 
                <><SpinningProgressBar />Analysing...</>
            :
                <><Sparkles />Analyse</>
            }
        </button>
    );
}

export default AnalyseButton;

function Sparkles() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" className="w-4 h-4">
            <path fillRule="evenodd" d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5ZM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5ZM16.5 15a.75.75 0 0 1 .712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 0 1 0 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 0 1-1.422 0l-.395-1.183a1.5 1.5 0 0 0-.948-.948l-1.183-.395a.75.75 0 0 1 0-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0 1 16.5 15Z" clipRule="evenodd" />
        </svg>

    )
}