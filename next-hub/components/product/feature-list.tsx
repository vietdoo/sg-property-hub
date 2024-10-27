import React from 'react';
export interface Feature {
    label: string;
    value: string | number | null;
    isUrl?: boolean; // Add this optional property
}

export interface Feature {
    label: string;
    value: string | number | null;
    isUrl?: boolean; // Add this optional property
}

interface FeatureListProps {
    features: Feature[];
}

const isValidUrl = (value: string): boolean => {
    try {
        new URL(value);
        return true;
    } catch (_) {
        return false;
    }
};


const FeatureList: React.FC<FeatureListProps> = ({ features }) => {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
            {features
                .filter(feature => {
                    const value = feature.value;
                    return value !== 'N/A' && value !== null && value !== undefined && value.toString().trim().length > 0;
                })
                .map((feature, index: number) => (
                    <div key={index} className="p-4 border rounded-lg shadow-md bg-white">
                        <h4 className="text-lg font-semibold mb-2 text-gray-800">{feature.label}</h4>
                        {typeof feature.value === 'string' && isValidUrl(feature.value) ? (
                            <a
                                href={feature.value}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 underline"
                            >
                                Xem
                            </a>
                        ) : (
                            <p className="text-gray-600">{feature.value ?? '--'}</p>
                        )}
                    </div>
                ))}
        </div>
    );
};

export default FeatureList;
