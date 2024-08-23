import React, { useEffect, useState } from 'react';
import { useAnalysedData } from '../AnalysedDataContext.js';
import { seedImageLoader } from './Utils.js';


function ImageBar() {

    const { data, updateAnalysedData } = useAnalysedData();
    const [selectedSeedIndex, setSelectedSeedIndex] = useState(null);
    const [seedImages, setSeedImages] = useState({});

    const updateActive = (id) => {
        updateAnalysedData({
            ...data,
            img: id
        });
        setSelectedSeedIndex(id);
    };

    const [loadedSeedImages, setLoadedSeedImages] = useState(false);

    useEffect(() => {

        if (data.state === "COMPLETE" && !loadedSeedImages) {
            data.response.annotations.forEach((annotation, index) => {
                if (annotation.label === 1) {
                    const seed_id = annotation.seed_id;
                    console.log("annotation, index", annotation, index);
                    console.log("seed_id", annotation.seed_id);
                    seedImageLoader(seed_id, data, (url) => {
                        setSeedImages(prevImages => ({ ...prevImages, [seed_id]: url }));
                    });
                }
            });
            setLoadedSeedImages(true);
        }
    }, [data.state]);

    useEffect(() => {
        if (data.state !== "COMPLETE") {
            setLoadedSeedImages(false);
        }
    }, [data.state]);

    return (
        <div className="relative z-0 flex w-full h-full bg-gray-800 px-3 rounded-xl shadow-lg">

            {/* CONTAINER 1 */}
            <div className='relative flex flex-col gap-y-2 items-start justify-center py-3 pl-4 pr-5'>
                {/* <div className='absolute left-0 z-20 min-w-4 w-4 h-full bg-gradient-to-r from-gray-800 to-gray-800/0' /> */}
                {/* <h1 className='text-xs font-semibold text-gray-400'>BATCH</h1> */}
                {data.state === "COMPLETE" ? (
                    <button
                    onClick={() => updateActive(data.root_image)}
                    className={`h-16 w-16 outline-none ${data.img === data.root_image ? "ring-[3px] ring-indigo-600" : ""} rounded-md`}
                    >
                        <img src={data.root_image} alt="batch" className='object-cover w-full h-full rounded-md' />
                    </button>
                ) : (
                    <div className='h-16 w-16 min-w-16 bg-gray-700/50 shadow-inner rounded-md' />
                )}
                
                {/* <div className='absolute right-0 z-20 min-w-4 w-4 h-full bg-gradient-to-r from-gray8050/0 to-gray-800' /> */}
            </div>

            <div className='relative w-[1px] bg-gray-700/80' />

            <div className='relative flex overflow-hidden items-start justify-center h-full'>

                {/* CONTAINER 3 */}
                <div className='absolute left-0 z-20 min-w-4 w-4 h-full bg-gradient-to-r from-gray-800 to-gray-800/0' />

                {/* CONTAINER 4 */}
                <div className='relative z-10 w-full h-full flex flex-col pt-3 items-start justify-center'>
                    {/*  */}
                    {/* <h1 className='text-xs font-semibold text-gray-400 pl-5'>SEEDS</h1> */}
                    {/* MAKE THIS BELOW SCROLL HORIZONTALLY */}

                    {data.state === "COMPLETE" ? (
                        <div className='flex gap-x-2 items-center w-full overflow-auto pl-5 pb-3 pt-2'>
                            {data.response.seed_indices
                                .flat()
                                .map(annotation_idx => data.response.annotations[annotation_idx])
                                .filter(annotation => annotation.label === 1)
                                .map((annotation) => (
                                    <button
                                        key={annotation.seed_id}
                                        onClick={() => updateActive(annotation.seed_id)}
                                        className={`h-16 w-16 outline-none flex-shrink-0 ${data.img === annotation.seed_id ? "ring-[3px] ring-indigo-600" : ""} rounded-md`}
                                    >
                                        <div className='h-16 w-16 object-cover w-full h-full rounded-md bg-black'>
                                            <SeedbarImage data={data} seedIndex={annotation.seed_id} isSelected={annotation.seed_id === selectedSeedIndex} imageUrl={seedImages[annotation.seed_id]} />
                                        </div>
                                    </button>
                                ))
                            }
                            <div className='h-16 w-16 min-w-16 bg-transparent rounded-md border-dashed border-2 border-gray-700/70' />
                        </div>
                    ) : (
                        <div className='flex gap-x-2 items-center w-full overflow-auto pl-5 pb-3 pt-2'>
                            {Array.from({ length: 14 }, (_, i) => (
                                <div key={i} className='h-16 w-16 min-w-16 bg-gray-700/50 shadow-inner rounded-md' />
                            ))}
                        </div>
                    )}
                </div>
                <div className='absolute right-0 z-20 min-w-4 w-4 h-full bg-gradient-to-r from-gray-800/0 to-gray-800' />
            </div>
        </div>
    );
}


function SeedbarImage({ data, seedIndex, isSelected=true, size="SMALL", imageUrl }) {
    return (
        <div>
            {imageUrl && (
                <img src={imageUrl} alt="SEED" className={`${size == "BIG" ? "h-64 w-64" : "h-16 w-16"} object-cover rounded-md overflow-hidden`} />
            )}
        </div>
    );
}

export { ImageBar, SeedbarImage };