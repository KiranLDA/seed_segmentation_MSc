import React, { useEffect, useState } from "react";
import ConfigDrop from "./Config";
import { useAnalysedData } from '../AnalysedDataContext.js';
import { classifier, countMaskLabels } from './Utils.js';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import ThresholdSliderArea from "./ThresholdSlider.js";
import {Histogram} from "./Histogram.js";


function StatisticsBar() {

    const { data, updateAnalysedData } = useAnalysedData();
    const [classifications, setClassifications] = useState(data.classifications);

    useEffect(() => {
        setClassifications(data.classifications);
    }, [data.classifications]);

    const toggleClassification = (img) => {
        const nextClassification = {
            'FULL': 'PART',
            'PART': 'EMPTY',
            'EMPTY': 'INFESTED',
            'INFESTED': 'FULL'
        };
        const currentClassification = classifications[img];
        const updatedClassification = nextClassification[currentClassification];

        const updatedClassifications = {
            ...classifications,
            [img]: updatedClassification
        };

        setClassifications(updatedClassifications);
        // Optionally update the parent state if needed
        updateAnalysedData({
            ...data,
            classifications: updatedClassifications
        });
    };

    // on appear, calculate the statistics with the classifier function and store it in the data object
    useEffect(() => {
        if (data.state === "COMPLETE") {
            const { classifications, classification_count, seed_health_dict } = classifier(data);
            updateAnalysedData({
                ...data,
                classifications: classifications,
                classification_count: classification_count,
                seed_health_dict: seed_health_dict
            });
        }
    }, [data.state, data.thresholds]);

    const [seedIsInfested, setSeedIsInfested] = useState(false);
    const [meanIntensity, setMeanIntensity] = useState(0);

    const checkInfestation = () => {
        if (data.state !== "COMPLETE") return false;
        const seedAnnotations = data.response.annotations.filter(annotation => annotation.seed_id === data.img);
        return seedAnnotations.some(annotation => annotation.label === 4); // label 4 is INFESTATION
    };

    const getMeanIntensityOfEndosperm = () => {
        if (data.state !== "COMPLETE") return 0;
        const endospermAnnotations = data.response.annotations.filter(annotation => annotation.seed_id === data.img && annotation.label === 3);
        if (endospermAnnotations.length === 0) return 0;
        return endospermAnnotations[0].mean_intensity;
    };

    useEffect(() => {
        if (data.state === "COMPLETE") {
            setSeedIsInfested(checkInfestation());
            setMeanIntensity(getMeanIntensityOfEndosperm());
        }
    }, [data.state, data.img]);

    const downloadCSV = () => {
        // Define the headers and data for the CSV file
        const headers = 'ACCESSION ID, SEEDS, FULL, PART FULL, EMPTY, INFESTED\n';
        const seeds = data.response.seed_indices.length;
        const full = countClassifications(data, 'FULL');
        const partFull = countClassifications(data, 'PART');
        const empty = countClassifications(data, 'EMPTY');
        const infested = countClassifications(data, 'INFESTED');

        // Creating CSV content
        const csvContent = headers + `${data.batch_id}, ${seeds}, ${full}, ${partFull}, ${empty}, ${infested}`;

        // Create a Blob from the CSV Content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'exported_data.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const downloadCSVMasks = async () => {

        const zip = new JSZip();
        const csvRows = [
            ['mask_id', ...Object.keys(data.response.annotations[0])].join(',')
        ];

        data.response.annotations.forEach((obj, index) => {
            const row = [index, ...Object.values(obj).map(value => {
                if (Array.isArray(value)) {
                    return `"${value.join(';').replace(/"/g, '""')}"`;
                } else if (typeof value === 'string') {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            })].join(',');
            csvRows.push(row);

            if (obj.mask) {
                // Properly format the base64 string for conversion
                const base64Data = `data:image/png;base64,${obj.mask}`;
                const imgBlob = dataURItoBlob(base64Data);
                zip.file(`${data.batch_id}_mask_${index}.png`, imgBlob);
            }
        });

        const csvContent = csvRows.join('\n');
        zip.file("annotations.csv", csvContent);

        const content = await zip.generateAsync({type:"blob"});
        saveAs(content, `mask_data_${data.batch_id}.zip`);
    
    };
    
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(',')[1]);
        const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], {type: mimeString});
    }


    function countClassifications(data, classification_idx) {
        let count = 0;
        for (const classification of Object.values(data.classifications)) {
            if (classification === classification_idx) {
                count++;
            }
        }
        return count;
    }


    return (
        <div className="flex flex-col w-full h-full py-4 px-8 gap-y-4">

            <div className="flex justify-between items-center">
                <div className="flex justify-start w-full gap-x-10">
                    <div className='flex flex-col justify-items-start'>
                        <div className="text-xs font-bold text-gray-400" onClick={() => {console.log(data); console.log(countMaskLabels(data))}}>
                            IMAGE NAME
                        </div>
                        {/* IF LOADING OR EMPTY... */}
                        {data.state === "EMPTY" || data.state === "LOADING" ? (
                            <div className="h-10 bg-gray-600/60 rounded-md w-24 mt-2" />
                        ) : (
                            <div className="text-white text-lg font-semibold">
                                {data.batch_id.length > 15 ? `${data.batch_id.substring(0, 15)}...` : data.batch_id}
                            </div>
                        )}
                    </div>
                    <div className='flex flex-col justify-items-start'>   
                        <div className="text-xs font-bold text-gray-400">
                            SEEDS
                        </div>
                        {/* IF LOADING OR EMPTY... */}
                        {data.state === "EMPTY" || data.state === "LOADING" ? (
                            <div className="h-10 bg-gray-600/60 rounded-md w-24 mt-2" />
                        ) : (
                            <div className="text-white text-lg font-semibold">
                                {data.response.seed_indices.length}
                            </div>
                        )}
                    </div>
                </div>
                <div className={`flex items-center gap-x-4 ${data.state !== "COMPLETE" ? "opacity-50" : ""}`}>
                    <button onClick={downloadCSV}  title="Download Classification Data" disabled={data.state !== "COMPLETE"}>
                        <DownloadIcon />
                    </button>
                    <button title="Download Mask Data" onClick={downloadCSVMasks} disabled={data.state !== "COMPLETE"}>
                        <DownloadIcon2 />
                    </button>
                </div>
            </div>

            {/* FIRST LINE */}
            <div className={`flex justify-start w-full ${data.img !== data.root_image ? "gap-x-12" : "gap-x-10"}`}>

                <div className='flex flex-col justify-items-start'>   
                    <div className="text-xs font-bold text-gray-400">
                        {data.img === data.root_image ? "FULL" : "ID"}
                    </div>
                    {/* IF LOADING OR EMPTY... */}
                    {data.state === "EMPTY" || data.state === "LOADING" ? (
                        <div className="h-10 bg-gray-600/60 rounded-md w-24 mt-2" />
                    ) : (
                        <>
                            {data.classification_count !== undefined && (
                                <div className={`${data.img === data.root_image ? 'flex items-center justify-center text-2xl font-bold text-green-800 w-12 bg-green-200 rounded-md mt-1' : 'text-3xl font-semibold text-white'}`}>
                                    {data.img === data.root_image ? countClassifications(data, 'FULL') : data.img}
                                </div>
                            )}
                        </>
                    )}
                </div>

                <div className={`flex flex-col justify-items-start ${data.img !== data.root_image ? "ml-4" : ""}`}>   
                    <div className="text-xs font-bold text-gray-400">
                        {data.img === data.root_image ? "PART FULL" : "CLASSIFICATION"}
                    </div>
                    {/* IF LOADING OR EMPTY... */}
                    {data.state === "LOADING" || data.state === "EMPTY" ? (
                        <div className="h-10 bg-gray-600/60 rounded-md w-24 mt-2" />
                    ) : (
                        
                        <div className={`text-3xl font-semibold text-white`}>
                            {data.classification_count !== undefined && (
                                <div className="flex items-center">
                                    {data.img === data.root_image ? (
                                        <div className='flex items-center justify-center text-2xl font-bold text-blue-800 w-12 bg-blue-200 rounded-md mt-1'>
                                            {countClassifications(data, 'PART')}
                                        </div>
                                    ) : (
                                        <button
                                            className={`flex text-sm font-black ${classifications[data.img] === 'FULL' ? 'text-green-800 bg-green-200' : classifications[data.img] === 'PART' ? 'text-blue-800 bg-blue-200' : classifications[data.img] === 'EMPTY' ? 'text-yellow-800 bg-yellow-200' : 'text-red-800 bg-red-200'} rounded-md mt-1 px-2`}
                                            onClick={() => toggleClassification(data.img)}
                                        >
                                            {classifications[data.img]}
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className='flex flex-col justify-items-start'>   
                    <div className="text-xs font-bold text-gray-400">
                        <div className="text-xs font-bold text-gray-400">
                            {data.img === data.root_image ? "EMPTY" : ""}
                        </div>
                    </div>
                        {/* IF LOADING OR EMPTY... */}
                        {data.state === "LOADING" || data.state === "EMPTY" ? (
                            <div className="h-10 bg-gray-600/0 rounded-md w-24 mt-2" />
                        ) : (
                            <div className="text-3xl font-semibold text-white">
                                {data.classification_count !== undefined && (
                                    <div className={`${data.img === data.root_image ? 'flex items-center justify-center text-2xl font-bold text-yellow-800 w-12 bg-yellow-200 rounded-md mt-1' : 'text-3xl h-full font-semibold text-white'}`}>
                                        {data.img === data.root_image ? countClassifications(data, 'EMPTY') : ``}
                                    </div>
                                )}
                            </div>
                        )}
                </div>

                {data.img === data.root_image && (
                    <div className='flex flex-col justify-items-start'>   
                        <div className="text-xs font-bold text-gray-400">
                            <div className="text-xs font-bold text-gray-400">
                                INFESTED
                            </div>
                        </div>
                            {/* IF LOADING OR EMPTY... */}
                            {data.state === "LOADING" || data.state === "EMPTY" ? (
                                <div className="h-10 bg-gray-600/60 rounded-md w-24 mt-2" />
                            ) : (
                                <div className="text-3xl font-semibold text-white">
                                    {data.classification_count !== undefined && (
                                        <div className='flex items-center justify-center text-2xl font-bold text-red-800 w-12 bg-red-200 rounded-md mt-1'>
                                            {countClassifications(data, 'INFESTED')}
                                        </div>
                                    )}
                                </div>
                            )}
                    </div>
                )}
            </div>

            <hr className="border-t border-gray-300/30 w-full my-1" />

            <div className="relative flex flex-col w-full h-full items-start justify-start flex-grow">
                <div className="flex flex-col flex-grow w-full h-full items-start justify-start">
                    {data.state === "COMPLETE" && (
                        data.img === data.root_image ? (
                            <>
                                <p className="text-xs font-semibold text-gray-400 mb-2">CLASSIFICATION THRESHOLD</p>
                                <div className="w-full mb-2">
                                    <ThresholdSliderArea />
                                </div>
                                <p className="text-xs font-semibold text-gray-400 mb-2 mt-2">DISTRIBUTION OF SEED FULLNESS</p>
                                <div className="flex flex-col justify-between w-full h-full bg-gray-700/50 rounded-md pt-4 px-4 mt-2">
                                    <Histogram />
                                </div>
                            </>
                        ) : (
                            <>
                                
                                <p className="text-xs font-semibold text-gray-400">SEED STATISTICS</p>
                                
                                <div className="flex flex-row justify-between w-full mb-2">
                                    <div className="flex justify-start items-center text-sm font-medium text-white">
                                        <p className='text-xs font-semibold text-white mr-4'>SEED FULLNESS</p>
                                        <div className={`text-lg font-semibold px-1 py-0.5 rounded-md`}>
                                            {isNaN(data.seed_health_dict[data.img]) ? '' : `${(data.seed_health_dict[data.img] * 100).toFixed(1)}%`}
                                        </div>
                                    </div>
                                    <div className="flex justify-start items-center text-sm font-medium text-white">
                                        <p className='text-xs font-semibold text-white mr-4'>ENDOSPERM INTENSITY</p>
                                        <div className={`text-lg font-semibold px-1 py-0.5 rounded-md`}>
                                            {isNaN(meanIntensity) ? '' : `${((meanIntensity/255).toFixed(3) * 100).toFixed(1)}%`}
                                        </div>
                                    </div>
                                </div>

                                <p className="text-xs font-semibold text-gray-400 mt-2 mb-2">DISTRIBUTION OF SEED FULLNESS</p>
                                <div className="flex flex-col justify-between w-full h-full bg-gray-700/50 rounded-md pt-4 px-4 mt-2">
                                    <Histogram />
                                </div>
                            </>
                        )
                    )}
                    

                </div>
                
            </div>
        </div>
    );
}


function DownloadIcon2() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" class="w-6 h-6">
        <path d="M6 3a3 3 0 0 0-3 3v1.5a.75.75 0 0 0 1.5 0V6A1.5 1.5 0 0 1 6 4.5h1.5a.75.75 0 0 0 0-1.5H6ZM16.5 3a.75.75 0 0 0 0 1.5H18A1.5 1.5 0 0 1 19.5 6v1.5a.75.75 0 0 0 1.5 0V6a3 3 0 0 0-3-3h-1.5ZM12 8.25a3.75 3.75 0 1 0 0 7.5 3.75 3.75 0 0 0 0-7.5ZM4.5 16.5a.75.75 0 0 0-1.5 0V18a3 3 0 0 0 3 3h1.5a.75.75 0 0 0 0-1.5H6A1.5 1.5 0 0 1 4.5 18v-1.5ZM21 16.5a.75.75 0 0 0-1.5 0V18a1.5 1.5 0 0 1-1.5 1.5h-1.5a.75.75 0 0 0 0 1.5H18a3 3 0 0 0 3-3v-1.5Z" />
        </svg>
    );
}


function DownloadIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" class="w-6 h-6">
        <path fill-rule="evenodd" d="M1.5 5.625c0-1.036.84-1.875 1.875-1.875h17.25c1.035 0 1.875.84 1.875 1.875v12.75c0 1.035-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 0 1 1.5 18.375V5.625ZM21 9.375A.375.375 0 0 0 20.625 9h-7.5a.375.375 0 0 0-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 0 0 .375-.375v-1.5Zm0 3.75a.375.375 0 0 0-.375-.375h-7.5a.375.375 0 0 0-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 0 0 .375-.375v-1.5Zm0 3.75a.375.375 0 0 0-.375-.375h-7.5a.375.375 0 0 0-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 0 0 .375-.375v-1.5ZM10.875 18.75a.375.375 0 0 0 .375-.375v-1.5a.375.375 0 0 0-.375-.375h-7.5a.375.375 0 0 0-.375.375v1.5c0 .207.168.375.375.375h7.5ZM3.375 15h7.5a.375.375 0 0 0 .375-.375v-1.5a.375.375 0 0 0-.375-.375h-7.5a.375.375 0 0 0-.375.375v1.5c0 .207.168.375.375.375Zm0-3.75h7.5a.375.375 0 0 0 .375-.375v-1.5A.375.375 0 0 0 10.875 9h-7.5A.375.375 0 0 0 3 9.375v1.5c0 .207.168.375.375.375Z" clip-rule="evenodd" />
        </svg>
    );
}


  
  export default StatisticsBar;