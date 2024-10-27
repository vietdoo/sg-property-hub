// import { Map } from "@components"
import dynamic from "next/dynamic";
import { fetchHouses } from "@utils";
import { HomeProps } from "@types";
import { propDist, propType } from "@constants";
import { HouseCard, Pagination, SearchBar, CustomFilter, Hero } from "@components";
import { useRouter } from "next/router";
import { usePathname } from "next/navigation";

const LazyMap = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => <p>Loading...</p>,
});

export default async function Maps({ searchParams }: HomeProps) {
  const allHouses = await fetchHouses({
    page: searchParams.page || 1
  });

  const maxPages = 20;
  const isDataEmpty = !Array.isArray(allHouses) || allHouses.length < 1 || !allHouses;
  
  return (
    <main className='overflow-hidden' >
    <div>
      <LazyMap />
    </div>
    <div className='mt-12 padding-x padding-y max-width' id='discover'>
      {!isDataEmpty ? (
        <section>
          <div className='home__houses-wrapper'>
            {allHouses?.map((house) => (
              <HouseCard house={house} />
            ))}
          </div>

          {/* <Pagination
            page={(searchParams.page || 1) / 1}
            maxPages={maxPages}
            isNext={allHouses.length > 0}
          /> */}
        </section>
      ) : (
        <div className='home__error-container'>
          <h2 className='text-black text-xl font-bold'>Không tìm thấy bất động sản phù hợp</h2>
          <p>{allHouses?.message}</p>
        </div>
      )}
    </div>
    </main>
    
  )
}

