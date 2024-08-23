import React from 'react';

const SpinningProgressBar = () => {
    return (
        <span className="flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-white opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
        </span>
    );
};

export default SpinningProgressBar;
