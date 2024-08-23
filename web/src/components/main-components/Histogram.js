import React from 'react';
import { useAnalysedData } from '../AnalysedDataContext.js';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
      position: 'top',
    },
    title: {
      display: false,
      text: 'Histogram of Mean Intensity',
    },
  },
  scales: {
    x: {
      stacked: true,
      display: true,
      title: {
        display: true,
        text: 'Seed fullness (%)',
      },
      ticks: {
        display: true,
      },
      grid: {
        display: false,
      },
      min: 0,
      max: 100, // Make sure this is at least 100
    },
    y: {
      stacked: true,
      display: false,
      title: {
        display: false,
        text: 'Count',
      },
      ticks: {
        display: false,
      },
      grid: {
        display: false,
      },
    },
  },
};

const Histogram = () => {
    const epsilon = 0.0001;
    const { data } = useAnalysedData();
    const numBins = 20;
    const healthScores = Object.values(data.seed_health_dict).map(seed_health => parseFloat(seed_health));
    const binCounts = Array(numBins).fill(0);
    const binSize = 1 / (numBins);

    // Identify the seed id's for each classification
    const fullSeeds = Object.keys(data.classifications).filter(seed_id => data.classifications[seed_id] === 'FULL');
    const partSeeds = Object.keys(data.classifications).filter(seed_id => data.classifications[seed_id] === 'PART');
    const emptySeeds = Object.keys(data.classifications).filter(seed_id => data.classifications[seed_id] === 'EMPTY');
    const infestedSeeds = Object.keys(data.classifications).filter(seed_id => data.classifications[seed_id] === 'INFESTED');

    // Retrieve the health scores for those seeds
    const fullHealthScores = fullSeeds.map(seed_id => healthScores[seed_id]);
    const partHealthScores = partSeeds.map(seed_id => healthScores[seed_id]);
    const emptyHealthScores = emptySeeds.map(seed_id => healthScores[seed_id]);
    const infestedHealthScores = infestedSeeds.map(seed_id => healthScores[seed_id]);

    // Calculate the bin counts for each of the three classifications
    fullHealthScores.forEach(score => {
        if (score === null) {
            return;
        } else if (score !== 0) {
            score = score - epsilon;
        }
        const binIndex = Math.floor((score) / binSize);
        binCounts[binIndex]++;
    });
    const fullBinCounts = [...binCounts];

    binCounts.fill(0);
    partHealthScores.forEach(score => {
        if (score === null) {
            return;
        } else if (score !== 0) {
            score = score - epsilon;
        }
        const binIndex = Math.floor((score) / binSize);
        binCounts[binIndex]++;
    });
    const partBinCounts = [...binCounts];

    binCounts.fill(0);
    emptyHealthScores.forEach(score => {
        if (score === null) {
            return;
        } else if (score !== 0) {
            score = score - epsilon;
        }
        const binIndex = Math.floor((score) / binSize);
        binCounts[binIndex]++;
    });
    const emptyBinCounts = [...binCounts];

    binCounts.fill(0);
    infestedHealthScores.forEach(score => {
        if (score === null) {
            return;
        } else if (score !== 0) {
            score = score - epsilon;
        }
        const binIndex = Math.floor((score) / binSize);
        binCounts[binIndex]++;
    });
    const infestedBinCounts = [...binCounts];

    console.log(fullBinCounts.length, partBinCounts.length, emptyBinCounts.length, infestedBinCounts.length);

    const labels = Array.from({length: 20}, (_, i) => i * 5);
    console.log(labels);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: 'Full Seeds',
                data: fullBinCounts,
                backgroundColor: 'rgba(0, 128, 0, 0.5)',
            },
            {
                label: 'Part Full Seeds',
                data: partBinCounts,
                backgroundColor: 'rgba(0, 0, 255, 0.5)',
            },
            {
                label: 'Empty Seeds',
                data: emptyBinCounts,
                backgroundColor: 'rgba(255, 255, 0, 0.5)',
            },
            {
                label: 'Infested Seeds',
                data: infestedBinCounts,
                backgroundColor: 'rgba(255, 0, 0, 0.5)',
            },
        ],
    };
    return <Bar options={options} data={chartData} />;
};





const generateSeedHealthDictHistogram = (data, bins, classification) => {
    const epsilon = 0.0001;
    const histogramData = Array(bins).fill(0);
    data.response.seed_indices.forEach(seed => {
        const annotation = data.response.annotations[seed[0]];
        if (annotation.label === 1 && data.classifications[annotation.seed_id] === classification && data.seed_health_dict[annotation.seed_id] !== null) {
            var seed_health = parseFloat(data.seed_health_dict[annotation.seed_id]);
            const binIndex = Math.floor((seed_health-epsilon) * bins);
            histogramData[binIndex]++;
        }
    });
    return histogramData;
}


const HistogramArea = () => {
    const { data } = useAnalysedData();
    const numBins = 40;
    let histogramData_FULL = generateSeedHealthDictHistogram(data, numBins, 'FULL');
    let histogramData_PART = generateSeedHealthDictHistogram(data, numBins, 'PART');
    let histogramData_EMPTY = generateSeedHealthDictHistogram(data, numBins, 'EMPTY');
    let histogramData_INFESTED = generateSeedHealthDictHistogram(data, numBins, 'INFESTED');
    const length_of_all_histograms_combined = histogramData_FULL.length + histogramData_PART.length + histogramData_EMPTY.length + histogramData_INFESTED.length;

    let firstNonZeroIndex_FULL = histogramData_FULL.findIndex(count => count > 0);
    let firstNonZeroIndex_PART = histogramData_PART.findIndex(count => count > 0);
    let firstNonZeroIndex_EMPTY = histogramData_EMPTY.findIndex(count => count > 0);
    let firstNonZeroIndex_INFESTED = histogramData_INFESTED.findIndex(count => count > 0);

    let lastNonZeroIndex_FULL = histogramData_FULL.length - 1;
    while (lastNonZeroIndex_FULL >= 0 && histogramData_FULL[lastNonZeroIndex_FULL] === 0) {
        lastNonZeroIndex_FULL--;
    }
    
    let lastNonZeroIndex_PART = histogramData_PART.length - 1;
    while (lastNonZeroIndex_PART >= 0 && histogramData_PART[lastNonZeroIndex_PART] === 0) {
        lastNonZeroIndex_PART--;
    }
    
    let lastNonZeroIndex_EMPTY = histogramData_EMPTY.length - 1;
    while (lastNonZeroIndex_EMPTY >= 0 && histogramData_EMPTY[lastNonZeroIndex_EMPTY] === 0) {
        lastNonZeroIndex_EMPTY--;
    }
    
    let lastNonZeroIndex_INFESTED = histogramData_INFESTED.length - 1;
    while (lastNonZeroIndex_INFESTED >= 0 && histogramData_INFESTED[lastNonZeroIndex_INFESTED] === 0) {
        lastNonZeroIndex_INFESTED--;
    }

    let earliestNonZeroIndex = Math.min(firstNonZeroIndex_FULL, firstNonZeroIndex_PART, firstNonZeroIndex_EMPTY, firstNonZeroIndex_INFESTED);
    let latestNonZeroIndex = Math.max(lastNonZeroIndex_FULL, lastNonZeroIndex_PART, lastNonZeroIndex_EMPTY, lastNonZeroIndex_INFESTED);

    if (earliestNonZeroIndex === -1 || latestNonZeroIndex === -1) {
        earliestNonZeroIndex = 0;
        latestNonZeroIndex = 39;
    }

    histogramData_FULL = histogramData_FULL.slice(earliestNonZeroIndex, latestNonZeroIndex + 1);
    histogramData_PART = histogramData_PART.slice(earliestNonZeroIndex, latestNonZeroIndex + 1);
    histogramData_EMPTY = histogramData_EMPTY.slice(earliestNonZeroIndex, latestNonZeroIndex + 1);
    histogramData_INFESTED = histogramData_INFESTED.slice(earliestNonZeroIndex, latestNonZeroIndex + 1);

    console.log(earliestNonZeroIndex, latestNonZeroIndex, histogramData_FULL, histogramData_PART, histogramData_EMPTY, histogramData_INFESTED)
    
    const chartData = {
        labels: Array.from({length: length_of_all_histograms_combined}, (_, i) => Math.round(i * 1 / length_of_all_histograms_combined)),
        datasets: [
            {
                label: 'Mean Intensity',
                data: histogramData_FULL,
                backgroundColor: 'rgba(0, 128, 0, 0.5)',
            },
            {
                label: 'Mean Intensity',
                data: histogramData_PART,
                backgroundColor: 'rgba(0, 0, 255, 0.5)',
            },
            {
                label: 'Mean Intensity',
                data: histogramData_EMPTY,
                backgroundColor: 'rgba(255, 255, 0, 0.5)',
            },
            {
                label: 'Mean Intensity',
                data: histogramData_INFESTED,
                backgroundColor: 'rgba(255, 0, 0, 0.5)',
            },
        ],
    };
    return <Bar options={options} data={chartData} />;
};

export { HistogramArea, Histogram };
