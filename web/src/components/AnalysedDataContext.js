import React, { createContext, useState, useContext } from 'react';

export const AnalysedData = createContext();

const initialStructure = {
    state: "EMPTY", // ["EMPTY", "LOADING", "COMPLETE"]
    thresholds: {
        high: 0.65,
        low: 0.3,
    },
    classifications: {},
    classification_count: {FULL: 0, PART: 0, EMPTY: 0, INFESTED: 0},
    seed_health_dict: {},
    batch_id: null,
    response: null,
    root_image: null,
    image: null,
};

export const AnalysedDataProvider = ({ children }) => {

    const [data, setAnalysedData] = useState(initialStructure);

    const updateAnalysedData = (newData) => {
        setAnalysedData(prevData => ({ ...prevData, ...newData }));
    };

    return (
        <AnalysedData.Provider value={{ data, updateAnalysedData }}>
            {children}
        </AnalysedData.Provider>
    );
};

export const useAnalysedData = () => {
    const context = useContext(AnalysedData);
    if (context === undefined) {
        throw new Error('useRequestContext must be used within a RequestProvider');
    }
    return context;
};
