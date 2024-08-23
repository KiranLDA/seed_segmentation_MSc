import React, { useState, useEffect } from 'react';
import { seedImageLoader, seedMaskLoader } from './Utils.js';

function CroppedSeedImage({ data, seedIndex }) {
    const [imageUrl, setImageUrl] = useState(null);
    useEffect(() => {
        seedImageLoader(seedIndex, data, setImageUrl);
    }, [data, seedIndex]);
    return (
        <div>
            {imageUrl && <img src={imageUrl} alt="SEED" className='w-full h-full max-w-full max-h-full object-cover rounded-md overflow-hidden' style={{ aspectRatio: '1 / 1' }} />}
        </div>
    );
}

function SeedMaskMain({ data, seedIndex, maskIndex }) {
    const [maskUrl, setMaskUrl] = useState(null);
    useEffect(() => {
        seedMaskLoader(maskIndex, seedIndex, data, setMaskUrl);
    }, [data, seedIndex, maskIndex]);
    return (
        <div>
            {maskUrl && <img src={maskUrl} alt="SEED" className='w-full h-full max-w-full max-h-full object-cover rounded-md overflow-hidden' style={{ aspectRatio: '1 / 1' }} />}
        </div>
    );
}

export { CroppedSeedImage, SeedMaskMain };