import React from 'react';
import Main from './Main.js';
import Sidebar from './Sidebar.js';

export default function HomeContent() {

  return (
    <div className="fixed top-0 right-0 left-0 bottom-0 flex">
        <div className='w-1/4 z-10'>
            <Sidebar />
        </div>
        <div className='w-3/4 z-0'>
            <Main />
        </div>
    </div>
  );
}