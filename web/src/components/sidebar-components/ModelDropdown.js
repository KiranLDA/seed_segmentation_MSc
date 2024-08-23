import { useState, useContext } from 'react';
import { CheckIcon, ChevronUpDownIcon, BoltIcon, BugAntIcon } from '@heroicons/react/20/solid';
import { RequestContext } from '../RequestContext'; // Adjust the import to match your file structure

function ModelDropdown() {
  const [modelHovered, setModelHovered] = useState(null);
  const [isDropdownVisible, setIsDropdownVisible] = useState(false); // New state for dropdown visibility
  const { request, updateRequest } = useContext(RequestContext);
  const models = [{ name: 'YOLO', id: 1 }, { name: 'RCNN', id: 2 }];

  const setModel = (value) => {
    // Update model_id in request payload
    const newRequestObject = {
        ...request.payload,
        model_id: value,
    };
    updateRequest({
        ...request,
        payload: newRequestObject
    });
    setIsDropdownVisible(false);
  };

  const returnIcon = (model) => {
    switch (model) {
      case "YOLO":
        return <BugAntIcon className="h-4 w-4" aria-hidden="true" />;
      case "RCNN":
        return <BoltIcon className="h-4 w-4" aria-hidden="true" />;
      default:
        return <BoltIcon className="h-4 w-4" aria-hidden="true" />;
    }
  };

  return (
    <div className="relative rounded-md bg-gray-700/50 px-2 py-1 text-white mt-1">
      <div className="flex items-center" onClick={() => setIsDropdownVisible(!isDropdownVisible)}>
        {returnIcon(request.payload.model_id)}
        <span className="ml-3 block truncate text-sm">{request.payload.model_id}</span>
        <ChevronUpDownIcon className="h-5 w-5 text-gray-400 ml-auto" aria-hidden="true" />
      </div>

      {isDropdownVisible && (
        <div className="absolute flex flex-col z-10 mt-2 max-h-56 w-full overflow-auto rounded-md bg-gray-700 py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          onMouseLeave={() => setIsDropdownVisible(false)} // Hide dropdown when mouse leaves the area
        >
          {models.map((model) => (
            <button
              key={model.id}
              className={`relative select-none py-2 pl-3 pr-9 ${
                modelHovered === model.name ? 'bg-indigo-600 text-white' : 'text-white'
              }`}
              onMouseEnter={() => setModelHovered(model.name)}
              onMouseLeave={() => setModelHovered(null)}
              onClick={() => setModel(model.name)}
            >
              <div className="flex items-center">
                {returnIcon(model.name)}
                <span className={`ml-3 block truncate ${request.payload.model_id === model.name ? 'font-semibold' : 'font-normal'}`}>
                  {model.name}
                </span>
              </div>

              {request.payload.model_id === model.name && (
                <CheckIcon className="h-5 w-5 text-white absolute inset-y-0 right-0 flex items-center pr-4" aria-hidden="true" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default ModelDropdown;
