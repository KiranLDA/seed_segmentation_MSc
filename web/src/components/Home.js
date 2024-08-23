import React from 'react';
import { AnalysedDataProvider } from './AnalysedDataContext';
import HomeContent from './HomeContent';

function Home() {
  return (      
    <AnalysedDataProvider>
      <HomeContent />
    </AnalysedDataProvider>
  );
}

export default Home;