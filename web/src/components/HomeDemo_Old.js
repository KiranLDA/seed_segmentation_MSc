import React, { useState } from 'react';
import Main from './Main.js';
import Sidebar from './Sidebar.js';

const demoData_input = {
  active_id: 'BATCH_DEMO',
  show: 'EMPTY',
  threshold: 90,
  batch_id: '',
  data: {

    'BATCH_DEMO': {
      id: 'BATCH_DEMO',
      original: '/demo/batch/original.png',
      full: '/demo/batch/full.png',
      endosperm: '/demo/batch/endosperm.png',
      seedcoat: '/demo/batch/seed_coat.png',
      type: 'BATCH',
      statistics: {
        seeds: 9,
        avgFullness: 83.8,
      },
      notes: '',
    },

    'SEED1_DEMO': {
      id: 'SEED1_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 92.4,
      },
      notes: '',
    },

    'SEED2_DEMO': {
      id: 'SEED2_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 94.9,
      },
      notes: '',
    },

    'SEED3_DEMO': {
      id: 'SEED3_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 88.7,
      },
      notes: '',
    },

    'SEED4_DEMO': {
      id: 'SEED4_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 92.1,
      },
      notes: '',
    },

    'SEED5_DEMO': {
      id: 'SEED5_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 96.4,
      },
      notes: '',
    },

    'SEED6_DEMO': {
      id: 'SEED6_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 81.8,
      },
      notes: '',
    },

    'SEED7_DEMO': {
      id: 'SEED7_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 72.9,
      },
      notes: '',
    },

    'SEED8_DEMO': {
      id: 'SEED8_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 91.9,
      },
      notes: '',
    },

    'SEED9_DEMO': {
      id: 'SEED9_DEMO',
      full: '/demo/seed_1/full.png',
      endosperm: '/demo/seed_1/endosperm.png',
      seedcoat: '/demo/seed_1/seed_coat.png',
      type: 'SEED',
      statistics: {
        fullness: 94.3,
      },
      notes: '',
    },
  },
};

export const DemoContext = React.createContext();

function Home() {

  const [demoData, setDemoData] = useState(demoData_input);

  // Function to update demoData
  const updateDemoData = newData => {
    setDemoData(prevData => ({ ...prevData, ...newData }));
  };

  return (
    <DemoContext.Provider value={{ demoData, updateDemoData }}>
        <div className="fixed top-0 right-0 left-0 bottom-0 flex">
        <div className='w-1/4 z-10'>
          <Sidebar />
        </div>
        <div className='w-3/4 z-0'>
          <Main />
        </div>
      </div>
    </DemoContext.Provider>
  );
}

export default Home;