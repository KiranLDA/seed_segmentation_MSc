import React, { useState, useRef, useEffect } from 'react';
import { useRequestContext } from '../RequestContext';

function UploadImage() {

    const [imageUrls, setImageUrls] = useState([]); // Store image URLs for display
    const { request, updateRequest } = useRequestContext();
    const [isHovered, setIsHovered] = useState(false);

    const handleImageUpload = (event) => {

        event.preventDefault(); // Prevent default behavior
        const files = Array.from(event.target.files || event.dataTransfer.files); // Support both input and drop
        const newImageUrls = files.map(file => URL.createObjectURL(file));
        setImageUrls([newImageUrls]);
        
        // Append the new files to the images array in the context
        const updatedImages = [...request.payload.images, ...files.map(file => file)];
        updateRequest({ payload: { ...request.payload, images: updatedImages } });
    };

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleMouseEnter = () => {
        setIsHovered(true);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
    };

    const ref = useRef(null);
    useEffect(() => {
        const adjustHeight = () => {
            if (ref.current) {
            ref.current.style.height = `${ref.current.offsetWidth}px`;
            }
        };

        // Adjust height on mount and window resize
        adjustHeight();
        window.addEventListener('resize', adjustHeight);

        // Cleanup listener
        return () => window.removeEventListener('resize', adjustHeight);
    }, []);

    return (
        <div className='w-full h-full' ref={ref}>
            {imageUrls[0] ? 
                <div className='relative w-full h-full' onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
                    <div className='relative w-full h-full overflow-hidden'>
                        <img src={imageUrls[0]} alt="Uploaded" className='object-cover object-center w-full h-full rounded-md'/> 
                    </div>
                    {isHovered && 
                        <button
                        onClick={() => {
                            // Clear image URLs
                            setImageUrls([null]);
                            
                            // Update request context to add null to images array
                            const updatedImages = [...request.payload.images, ...[null]];
                            updateRequest({ payload: { ...request.payload, images: updatedImages } });
                        }}
                        className='absolute -top-2 -right-2 p-[0.5px] bg-white rounded-full border border-gray-600 hover:bg-gray-100 cursor-pointer'
                        >
                            <Cross currentColor={'#1F2937'}/>
                        </button>
                    }
                </div>
                : 
                <div className='w-full h-full bg-gray-700/50 shadow-inner rounded-md'
                     onDragOver={handleDragOver} onDrop={handleImageUpload}>
                    <input type="file" accept=".png, .jpeg, .jpg" onChange={handleImageUpload} style={{ display: 'none' }} id="imageUpload" />
                    <label htmlFor="imageUpload" className='flex cursor-pointer justify-center items-center h-full w-full gap-2'>
                        <Plus />
                        <p className='text-sm font-medium text-white'>Upload Image</p>
                    </label>
                </div>
            }
        </div>
    );
}

export default UploadImage;


function Plus() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="white" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
    )
}

function Cross({ currentColor }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke={currentColor} className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
    );
}