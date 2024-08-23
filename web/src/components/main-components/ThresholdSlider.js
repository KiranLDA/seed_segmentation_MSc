import React, { useState } from "react";
import { useAnalysedData } from '../AnalysedDataContext.js';

export default function ThresholdSliderArea() {
    const { data, updateAnalysedData } = useAnalysedData();
    const [localThresholdLow, setLocalThresholdLow] = useState(Math.round(data.thresholds.low * 100));
    const [localThresholdHigh, setLocalThresholdHigh] = useState(Math.round(data.thresholds.high * 100));

    const handleThresholdChange = () => {
        const lowNum = parseInt(localThresholdLow, 10);
        const highNum = parseInt(localThresholdHigh, 10);
        let updatedLow = lowNum >= 0 && lowNum <= 100 && lowNum < highNum ? lowNum : Math.round(data.thresholds.low * 100);
        let updatedHigh = highNum >= 0 && highNum <= 100 && highNum > lowNum ? highNum : Math.round(data.thresholds.high * 100);

        setLocalThresholdLow(updatedLow);
        setLocalThresholdHigh(updatedHigh);

        if (updatedLow !== Math.round(data.thresholds.low * 100) || updatedHigh !== Math.round(data.thresholds.high * 100)) {
            updateAnalysedData({ ...data, thresholds: { low: updatedLow / 100, high: updatedHigh / 100 } });
        }
    };

    const isButtonDisabled = localThresholdLow === Math.round(data.thresholds.low * 100) && localThresholdHigh === Math.round(data.thresholds.high * 100);

    return (
        <div className="flex justify-between items-start">
            <div className="flex justify-start items-start">
                <div className="flex justify-start w-32 items-center text-sm font-medium text-white mr-6">
                    <p className='font-semibold text-xs'>EMPTY</p>
                    <div className="flex items-center">
                        <input 
                            type="text"
                            className='text-lg bg-transparent border-none text-white w-16 text-right outline-none'
                            value={localThresholdLow}
                            onChange={(e) => setLocalThresholdLow(e.target.value)}
                        />
                        <p className='text-gray-500 text-xs'>%</p>
                    </div>
                </div>
                <div className="flex justify-start w-32 items-center text-sm font-medium text-white">
                    <p className='font-semibold text-xs'>FULL</p>
                    <div className="flex items-center">
                        <input 
                            type="text"
                            className='text-lg bg-transparent border-none text-white w-16 text-right outline-none'
                            value={localThresholdHigh}
                            onChange={(e) => setLocalThresholdHigh(e.target.value)}
                        />
                        <p className='text-gray-500 text-xs'>%</p>
                    </div>
                </div>
            </div>
        
            <button 
                className={`text-xs ${isButtonDisabled ? 'bg-gray-500/50' : 'bg-indigo-600 hover:bg-indigo-700'} text-white font-bold py-1 px-2 rounded-md`}
                onClick={handleThresholdChange}
                disabled={isButtonDisabled}
            >
                Re-calculate
            </button>
        </div>
    );
}
