import React from 'react';
import {ImageBar} from './main-components/ImageBar.js';
import MainAnalysisTab from './main-components/MainAnalysisTab.js';

function Main() {
    return (
        <div className='flex flex-col gap-y-0 w-full h-full bg-gray-700/90'>
            <div className='flex justify-center items-center py-4 mt-2 w-full h-4/5 px-12'>
                <MainAnalysisTab />
            </div>
            <div className='w-full h-1/5'>
                <div className='px-12'>
                    <ImageBar />
                </div>
            </div>
        </div>
    );
  }
  
  export default Main;