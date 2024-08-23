import React, { createContext, useState, useContext } from 'react';

export const RequestContext = createContext();

const initialRequest = {
    state: "EMPTY",
    payload: {
        "batch_id": "",
        "model_id": "RCNN",
        "images": [],
    },
};

export const RequestProvider = ({ children }) => {

    const [request, setRequest] = useState(initialRequest);

    const updateRequest = (newData) => {
        setRequest(prevData => ({ ...prevData, ...newData }));
    };

    return (
        <RequestContext.Provider value={{ request, updateRequest }}>
            {children}
        </RequestContext.Provider>
    );
};

export const useRequestContext = () => {
    const context = useContext(RequestContext);
    if (context === undefined) {
        throw new Error('useRequestContext must be used within a RequestProvider');
    }
    return context;
};
