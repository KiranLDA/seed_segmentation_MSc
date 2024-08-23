import React, { useState, useEffect } from 'react';
import StatisticsBar from './StatisticsBar.js';
import { useAnalysedData } from '../AnalysedDataContext.js';
import { seedClassificationLoader } from './Utils.js';
import { CroppedSeedImage, SeedMaskMain } from './ImageOverlayLoaders.js';

function MainAnalysisTab() {
    const { data } = useAnalysedData();
    const [partShowing, setPartShowing] = useState([]);
    const [partHovered, setPartHovered] = useState();
    const [classificationImages, setClassificationImages] = useState({});
    const [classificationShowing, setClassificationShowing] = useState([]);
    const [classificationHovered, setClassificationHovered] = useState();

    useEffect(() => {
        if (data.state === "COMPLETE") {
            const classifications = ['FULL', 'PART', 'EMPTY', 'INFESTED'];
            const promises = classifications.map(classification =>
                new Promise(resolve => {
                    seedClassificationLoader(classification, data, url => {
                        setClassificationImages(prev => ({ ...prev, [classification]: url }));
                        resolve();
                    });
                })
            );
            Promise.all(promises);
        }
    }, [data.classification_count, data.threshold]);

    const toggleShowing = (item, showingState, setShowingState) => {
        setShowingState(showingState.includes(item) ? showingState.filter(i => i !== item) : [...showingState, item]);
    };

    const handleMouseEvents = (item, setHovered) => ({
        onMouseEnter: () => setHovered(item),
        onMouseLeave: () => setHovered(null)
    });

    const maskNames = ["COAT", "INTERIOR", "ENDOSPERM", "INFESTED", "VOID"]

    const renderButtons = (type, items, showingState, setShowingState, hoveredState, setHoveredState, colorMap) => (
        items.map(item => (
            <button
                key={item}
                onClick={() => toggleShowing(item, showingState, setShowingState)}
                {...handleMouseEvents(item, setHoveredState)}
                className={`font-bold text-xs px-2 outline-none ${showingState.includes(item) ? colorMap[item] : hoveredState === item ? colorMap.hover : colorMap.default}`}
            >
                {type === "MASK" ? maskNames[item - 1] : item}
            </button>
        ))
    );

    const maskColorMap = {
        1: 'text-purple-500', // COAT
        2: 'text-blue-500', // INTERIOR
        3: 'text-green-500', // ENDOSPERM
        4: 'text-red-500', // INFESTED
        5: 'text-yellow-500', // VOID
        hover: 'text-gray-500',
        default: 'text-gray-700'
    };

    const classificationColorMap = {
        FULL: 'text-white', // COAT
        PART: 'text-white', // INTERIOR
        EMPTY: 'text-white', // ENDOSPERM
        INFESTED: 'text-white', // INFESTED
        hover: 'text-gray-500',
        default: 'text-gray-700'
    };

    return (
        <div className='flex w-full h-full justify-between bg-gray-800 rounded-md'>
            <div className='h-full w-full'>
                <StatisticsBar />
            </div>
            <div className='flex w-full h-full'>
                {data.state === "COMPLETE" ? (
                    <div className='relative w-full h-full bg-black rounded-md'>
                        <div className='absolute top-0 left-0 w-full h-full'>
                            {data.img === data.root_image ? (
                                <>
                                    <img src={data.img} className='object-cover w-full h-full rounded-md opacity-100' />
                                    {classificationShowing.map(classification => (
                                        <img key={classification} src={classificationImages[classification]} className='absolute top-0 left-0 w-full h-full object-cover rounded-md opacity-100' />
                                    ))}
                                </>
                            ) : (
                                <>
                                    <CroppedSeedImage data={data} seedIndex={data.img} />
                                    {partShowing.map(part => (
                                        <div className='absolute top-0 left-0 w-full h-full object-cover rounded-md opacity-100' >
                                            <SeedMaskMain key={part} data={data} seedIndex={data.img} maskIndex={part} />
                                        </div>
                                    ))}
                                </>
                            )}
                        </div>
                        <div className='absolute bottom-0 left-0 flex pb-2'>
                            {data.img === data.root_image ?
                                renderButtons('CLASSIFICATION', ['FULL', 'PART', 'EMPTY', 'INFESTED'], classificationShowing, setClassificationShowing, classificationHovered, setClassificationHovered, classificationColorMap) :
                                renderButtons('MASK', [1, 2, 3, 4, 5], partShowing, setPartShowing, partHovered, setPartHovered, maskColorMap)
                            }
                        </div>
                    </div>
                ) : (
                    <div className='flex flex-col w-full h-full bg-gray-700/50 rounded-md mb-4' />
                )}
            </div>
        </div>
    );
}

export default MainAnalysisTab;

