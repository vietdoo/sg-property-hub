// "use client";

// import { useState } from "react";
// import { useRouter } from "next/navigation";
// import { Dialog } from "@headlessui/react";
// import { Slider } from "@nextui-org/react";
// import { PriceCustomFilterProps } from "@types";
// import { updateSearchParams } from "@utils";

// export default function PriceCustomFilter({ title, minPrice, maxPrice }: PriceCustomFilterProps) {
//     const router = useRouter();
//     const [isOpen, setIsOpen] = useState(false);
//     const [values, setValues] = useState<[number, number]>([minPrice, maxPrice]);

//     // Update the URL search parameters and navigate to the new URL
//     const handleUpdateParams = (min: number, max: number) => {
//         const newPathName = updateSearchParams('lowest_price', min.toString(), 'highest_price', max.toString());
//         router.push(newPathName);
//     };

//     const handleApply = () => {
//         handleUpdateParams(values[0], values[1]);
//         setIsOpen(false);
//     };

//     return (
//         <div className="relative">
//             <button
//                 onClick={() => setIsOpen(true)}
//                 className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg focus:outline-none"
//             >
//                 {title}
//             </button>
//             <Dialog open={isOpen} onClose={() => setIsOpen(false)}>
//                 <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
//                 <div className="fixed inset-0 flex items-center justify-center p-4">
//                     <Dialog.Panel className="bg-white rounded-lg p-6 shadow-lg w-full max-w-md">
//                         <Dialog.Title className="text-lg font-semibold mb-4">Select Price Range</Dialog.Title>
//                         <div className="flex justify-between text-gray-700 mb-4">
//                             <span>{values[0].toLocaleString()} VND</span>
//                             <span>{values[1].toLocaleString()} VND</span>
//                         </div>
//                         <Slider
//                             label="Price Range"
//                             step={1000000}
//                             minValue={minPrice}
//                             maxValue={maxPrice}
//                             defaultValue={[minPrice, maxPrice]}
//                             formatOptions={{ style: "currency", currency: "VND" }}
//                             value={values}
//                             onChange={(newValue) => setValues(newValue as [number, number])}
//                             className="max-w-md"
//                         />
//                         <div className="flex justify-end mt-4">
//                             <button
//                                 onClick={() => setIsOpen(false)}
//                                 className="bg-gray-300 text-gray-800 py-2 px-4 rounded-lg mr-2"
//                             >
//                                 Cancel
//                             </button>
//                             <button
//                                 onClick={handleApply}
//                                 className="bg-blue-500 text-white py-2 px-4 rounded-lg"
//                             >
//                                 Apply
//                             </button>
//                         </div>
//                     </Dialog.Panel>
//                 </div>
//             </Dialog>
//         </div>
//     );
// }

export default function PriceCustomFilter() {
    return (
        <div>
            <p>p1</p>
        </div>
    );
}