import React from "react";
import { useRequestContext } from "../RequestContext";
import { data, useAnalysedData } from "../AnalysedDataContext";
import UploadImage from "./UploadImage";
import AnalyseButton from "./AnalyseButton";
import ModelDropdown from "./ModelDropdown";

export default function SidebarForm() {

    const { request, updateRequest } = useRequestContext();
    const { data, updateAnalysedData } = useAnalysedData();
    const handleBatchIdChange = (event) => {
        const newRequestObject = {
            ...request.payload,
            batch_id: event.target.value,
        };
        updateRequest({
            ...request,
            payload: newRequestObject
        });
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col w-full items-start justify-start">
                <p className="text-xs font-semibold text-gray-400 ml-2">MODEL</p>
                {/* <div className="flex justify-center gap-x-[1px] w-full items-center mt-1">
                    {request.state === "COMPLETE" && <p className="text-gray-500/80 font-medium">#</p>}
                    <input 
                        type="text" 
                        className={`w-full text-white font-medium rounded-md outline-none py-2 px-2 ${request.state === "COMPLETE" ? 'bg-transparent' : (request.payload.batch_id ? 'bg-gray-500/50' : 'bg-gray-700/50')}`}
                        value={request.payload.batch_id}
                        onChange={handleBatchIdChange}
                        disabled={request.state === "COMPLETE"}
                    />
                </div> */}
                <div className="w-full h-full">
                    <ModelDropdown />
                </div>
            </div>
            {request.state === "LOADING" || request.state === "EMPTY" ? (
                <div>
                    <div className="flex flex-col w-full items-start justify-start mb-2">
                        <p className="text-xs font-semibold text-gray-400 ml-2 mb-1">X-RAY UPLOAD</p>
                        <UploadImage />
                    </div>
                    <AnalyseButton />
                </div>
            ) : (
                <button
                type="button"
                onClick={() => {
                updateRequest(resetRequest); 
                updateAnalysedData(resetResponse); 
                }}
                className="rounded-md w-full px-3.5 py-2.5 text-xs font-bold text-white shadow-sm bg-blue-900 hover:bg-blue-900"
                >
                    UPLOAD NEW BATCH
                </button>
            )}
        </div>
    )
}

const resetRequest = {
    state: "EMPTY",
    payload: {
        "batch_id": "",
        "model_id": "RCNN",
        "images": [],
    },
};


const resetResponse = {
    state: "EMPTY", // ["EMPTY", "LOADING", "COMPLETE"]
    thresholds: {
        high: 0.65,
        low: 0.3,
    },
    classifications: {},
    classification_count: {FULL: 0, PART: 0, EMPTY: 0, INFESTED: 0},
    batch_id: null,
    response: null,
    root_image: null,
    image: null,
};