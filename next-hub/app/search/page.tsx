import { fetchHouses } from "@utils";
import { HomeProps } from "@types";
import { propDist, propType, propCity } from "@constants";
import { HouseCard, Pagination, SearchBar, CustomFilter } from "@components";


export default async function Home({ searchParams }: HomeProps) {
  
  const allHouses = await fetchHouses({
    q: searchParams.q || '',
    page: searchParams.page || 1,
    city: searchParams.city,
    category: searchParams.category,

  });
  const maxPages = 20;
  const isDataEmpty = !Array.isArray(allHouses) || allHouses.length < 1 || !allHouses;

  return (
    <main className='overflow-hidden' >

      <div className='mt-12 padding-x padding-y max-width' id='discover'>
        <div className='home__text-container'>
          <h1 className='text-4xl font-extrabold'>Danh Sách Bất Động Sản</h1>
          <p>Tìm ngay bất động sản phù hợp với bạn</p>
        </div>

        <div className='home__filters'>
          <SearchBar />

          <div className='home__filter-container'>

            <CustomFilter title='category' options={propType} />
            <CustomFilter title='city' options={propCity} />
          </div>
        </div>

        {!isDataEmpty ? (
          <section>
            <div className='home__houses-wrapper'>
              {allHouses?.map((house) => (
                <HouseCard house={house} />
              ))}
            </div>

            <Pagination
              page={(searchParams.page || 1) / 1}
              maxPages={maxPages}
              isNext={allHouses.length > 0}
            />
          </section>
        ) : (
          <div className='home__error-container'>
            <h2 className='text-black text-xl font-bold'>Không tìm thấy bất động sản phù hợp</h2>
            <p>{allHouses?.message}</p>
          </div>
        )}
      </div>
    </main>
  );
}
