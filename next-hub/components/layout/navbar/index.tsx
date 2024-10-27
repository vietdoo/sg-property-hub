import Image from "next/image";
// "use client";
// import { useRouter } from 'next/router';

import CustomButton from "@components/CustomButton";

// import Cart from 'components/cart';
// import OpenCart from 'components/cart/open-cart';
import LogoSquare from '@components/logo-square';
// import { getMenu } from 'lib/shopify';
// import { Menu } from 'lib/shopify/types';
import Link from 'next/link';
import { Suspense } from 'react';
// import MobileMenu from './mobile-menu';
import Search from './search';

const SITE_NAME = 'SGP Hub';
import {
  ClerkProvider,
  SignedIn,
  SignedOut,
  UserButton,
  UserProfile
} from '@clerk/nextjs'

// import { currentUser } from '@clerk/nextjs/server';

// export interface NavbarProps {
//   is_login: boolean;
//   // user_button: any;
// }

export default async function Navbar() {
  // const user = await currentUser();
  // const user_name = user?.username ?? "";


  return (
    <nav className="relative flex items-center justify-between p-4 lg:px-6">
      <div className="block flex-none md:hidden">
      </div>
      <div className="flex w-full items-center">
        <div className="flex w-full md:w-1/3">
          <Link href="/" className="mr-2 flex w-full items-center justify-center md:w-auto lg:mr-6">
            <LogoSquare />
            <div className="ml-2 flex-none text-sm font-medium uppercase md:hidden lg:block">
              {SITE_NAME}
            </div>
          </Link>

        </div>
        <div className="hidden justify-center md:flex md:w-1/3">
          <Suspense>
            <Search />
          </Suspense>
         
        </div>
        
        <div className="flex justify-end md:w-1/3">
          <Suspense>
            <Link href="/maps" className="mr-5">
            <CustomButton
              title="Bản đồ"
              containerStyles="bg-primary-blue text-white rounded-full min-w-[110px]"
            />
            </Link>
            {/* <SignedOut>
              <Link href="/signin" className="mr-5">
                <CustomButton
                  title='Đăng nhập'
                  btnType='button'
                  containerStyles='text-primary-blue rounded-full bg-white min-w-[130px]'
                />
              </Link>
            </SignedOut> */}
            {/* <SignedIn>
              <UserButton />
   
              <Link href="/user/profile" className="mr-5">
                <CustomButton
                  title={user_name}
                  btnType='button'
                  containerStyles='text-primary-blue rounded-full bg-white'
                />
       
              </Link>
            </SignedIn> */}


          </Suspense>
        </div>
      </div>
    </nav>
  );
}

// const NavBar = () => (
  
//   <header className='w-full'>
//     <nav className='max-w-[1440px] mx-auto flex justify-between items-center sm:px-16 px-6 py-4 bg-transparent'>
//       <Link href='/' className='flex justify-center items-center'>
//         <Image
//           src='/logo_sgp.png'
//           alt='logo'
//           width={128}
//           height={25}
//           className='object-contain'
//         />
//       </Link>

//       <div className='flex justify-between'> 
//         <Link href="/maps" className="mr-5">
//           <CustomButton
//             title="Bản đồ"
//             containerStyles="bg-primary-blue text-white rounded-full min-w-[130px]"
//           />
//         </Link>
        

//         <CustomButton
//           title='Đăng nhập'
//           btnType='button'
//           containerStyles='text-primary-blue rounded-full bg-white min-w-[130px]'
//         />
//       </div>
      
    

//     </nav>
//   </header>
// );

// export default NavBar;
