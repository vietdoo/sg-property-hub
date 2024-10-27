
import Price from '@components/price';
import Prose from '@components/prose';

import { HouseProps } from "@types";
import { generatePrice } from "@utils";

export function ProductDescription({ product }: { product: HouseProps }) {
  
  return (
    <>
      <div className="mb-6 flex flex-col border-b pb-6 dark:border-neutral-700">
        <div className="text-lg font-bold text-gray-700 dark:text-gray-300 mb-1">
          {product.location_city}, {product.location_dist}
        </div>
        <h1 className="mb-2 text-3xl font-medium">{product.title}</h1>
        <div className="flex items-center mt-3">
          <div className="mr-auto w-auto rounded-full border border-blue-600 p-2 text-lg font-bold text-black">
            <Price
              amount={product.price !== null ? product.price.toString() : product.price_string}
              currencyCode='VND'
            />
          </div>
          <a
            href={product.url}
            target="_blank"
            className="ml-4 px-3 py-2 text-lg font-medium text-white bg-blue-500 rounded hover:bg-blue-600"
          >
            Xem ngay
          </a>
        </div>

      </div>


      {product.description ? (
        <div className="max-h-1/5 overflow-y-auto mb-6">
          <Prose
            className="text-2xl leading-tight dark:text-black/[80%]"
            html={product.description}
          />
        </div>
      ) : null}


    </>
  );
}