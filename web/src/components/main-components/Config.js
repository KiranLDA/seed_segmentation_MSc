import React, { useState, useEffect } from 'react'
import { useAnalysedData } from '../AnalysedDataContext.js';


export default function ConfigDrop() {

  const { data, updateAnalysedData } = useAnalysedData();
  
  const [localThreshold, setLocalThreshold] = useState(data.threshold);
  const [localBatchId, setLocalBatchId] = useState(data.batch_id);

  const handleSave = () => {
    updateAnalysedData({ ...data, threshold: localThreshold, batch_id: localBatchId });
  };

  useEffect(() => {
    setLocalThreshold(data.threshold);
    setLocalBatchId(data.batch_id);
  }, [data.threshold, data.batch_id]);

  return (
    <div>
      <Popover content={
        <div className="flex flex-col h-full justify-between gap-y-2">

            <h1 className="text-white text-xs font-bold border-b border-gray-500/70 py-2 px-4">CONFIGURATION</h1>

            <div className="flex justify-between items-center text-sm font-medium text-white px-4">
                <p className='font-semibold text-xs'>BATCH ID</p>
                <div className="flex items-center">
                    <input 
                      className='text-lg bg-transparent border-none text-white w-16 outline-none'
                      value={localBatchId}
                      onChange={(e) => setLocalBatchId(e.target.value)}
                    />
                </div>
            </div>

            <div className="flex justify-between items-center text-sm font-medium text-white px-4">
                <p className='font-semibold text-xs'>VIABILITY THRESHOLD</p>
                <div className="flex items-center">
                    <input 
                      type="text"
                      className='text-lg bg-transparent border-none text-white w-16 text-right outline-none'
                      value={localThreshold}
                      onChange={(e) => setLocalThreshold(e.target.value)}
                    />
                    <p className='text-gray-500 text-xs'>%</p>
                </div>
            </div>

            <button onClick={handleSave} className={`text-xs py-2 text-white font-bold rounded-b-md px-4 ${localThreshold === data.threshold && localBatchId === data.batch_id ? "bg-gray-400" : "bg-indigo-800"}`}>
                SAVE
            </button>

        </div>
    
      }>
        <Config />
      </Popover>
    </div>
  )
}

// <SliderComponent localThreshold={localThreshold} setLocalThreshold={setLocalThreshold} />

const Popover = ({ children, content }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative" onMouseEnter={() => setIsVisible(true)} onMouseLeave={() => setIsVisible(false)}>
      {children}
      {isVisible && (
        <div className="absolute z-10 w-64 h-48 bg-gray-800 border border-gray-500/70 rounded-md transform -translate-x-3/4">
          {content}
        </div>
      )}
    </div>
  );
};


// function SliderComponent({ localThreshold, setLocalThreshold }) {

//     const handleSliderChange = (event) => {
//         setLocalThreshold(event.target.value / 100);
//     };

//     function convertToPercentage(number) {
//         const multipliedNumber = Math.round(number * 100);
//         return multipliedNumber;
//     }

//     return (
//         <div className="flex flex-col mt-4 gap-2">
//             <div className="flex w-full justify-between items-center text-sm font-medium text-white">
//                 <p className='font-semibold'>Viability Threshold</p>
//                 <div className="flex items-start">
//                     <p className='text-xl'>{convertToPercentage(localThreshold)}</p>
//                     <p className='text-gray-200 text-xs mt-1'>%</p>
//                 </div>
//             </div>
//             <input 
//                 type="range" 
//                 min="0" 
//                 max="100" 
//                 step="1" 
//                 value={convertToPercentage(localThreshold)} 
//                 onChange={handleSliderChange}
//                 className=""
//             />
//         </div>
//     );
// }

function Config() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="white" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
        </svg>
    )
}