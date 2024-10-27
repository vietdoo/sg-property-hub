"use client";

import Image from "next/image";


import { CustomButton } from "@components";
import { text } from "stream/consumers";

const Hero = () => {
  const handleScroll = () => {
    const nextSection = document.getElementById("discover");

    if (nextSection) {
      nextSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="hero">
      <div className="hero__bg">
        <Image src="/bg.png" alt="hero" fill className="object-contain" layout="fill" style={{ objectFit: "cover", transform: 'scale(1.5)', zIndex: -1 }}/>
      </div>
      
      <div className="flex-1 pt-36 padding-x">
        <h1 className="hero__title">
          Tìm Nhà Siêu Dễ !
        </h1>

        <div className = 'hero__company' style={{ display: 'flex' }}>
          <div style={{ backgroundColor: 'black', padding: '10px', borderRadius: '20px' }}>
            <h1 style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>SG Property Hub</h1>
          </div>
        </div>


        <p className="hero__subtitle">
          Công cụ giúp bạn tìm được bất động sản phù hợp nhất
        </p>

        <CustomButton
          title="Khám phá ngay"
          containerStyles="bg-primary-blue text-white rounded-full mt-10"
          handleClick={handleScroll}
        />
      </div>
      <div className="hero__image-container">
        <div className="hero__image">
          <Image src="/hero-house5.png" alt="hero" fill className="object-contain" 
            style={{ transform: 'scale(1.0)', filter: 'drop-shadow(52px 52px 30px rgba(0, 0, 0, 0.5))' }}
          />
        </div>

        {/* <div className="hero__image-overlay">
          
        </div> */}
      </div>
    </div>
  );
};

export default Hero;
