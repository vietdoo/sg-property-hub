import { off } from "process";
import { MouseEventHandler } from "react";

export interface HouseProps {
  property_type: string;
  agent_agent_type: string | null;
  attr_built_year: number | null;
  attr_interior: string;
  location_address: string | null;
  project_name: string | null;
  description: string;
  publish_at: string;
  agent_email: string;
  attr_certificate: string;
  attr_length: number | null;
  location_city: string;
  project_profile: string | null;
  site: string;
  agent_name: string;
  attr_condition: string | null;
  attr_site_id: string | null;
  location_description: string | null;
  image: Array<string>;
  id: string;
  thumbnail: string;
  agent_phone_number: string;
  attr_direction: string | null;
  attr_total_area: number | null;
  location_dist: string;
  price: number;
  title: string;
  agent_profile: string | null;
  attr_feature: string;
  attr_total_room: number | null;
  location_lat: number;
  update_at: string;
  attr_area: number;
  attr_floor: number | null;
  attr_type_detail: string;
  location_long: number;
  initial_at: string;
  price_currency: string;
  initial_date: string;
  attr_bathroom: number | null;
  attr_floor_num: number | null;
  attr_width: number | null;
  location_street: string;
  url: string;
  price_string: string;
  agent_address: string | null;
  attr_bedroom: number | null;
  attr_height: number | null;
  location_ward: string;
}

export interface FilterProps {
  dist?: string;
  city?: string;
  category?: string;
  q?: string;
  limit?: number;
  fuel?: string;
  page?: number;
  offset?: number;
  lat_tl?: number;
  long_tl?: number;
  lat_br?: number;
  long_br?: number
}

export interface HomeProps {
  searchParams: FilterProps;
}

export interface CarCardProps {
  model: string;
  make: string;
  mpg: number;
  transmission: string;
  year: number;
  drive: string;
  cityMPG: number;
}

export interface CustomButtonProps {
  isDisabled?: boolean;
  btnType?: "button" | "submit";
  containerStyles?: string;
  textStyles?: string;
  title: string;
  rightIcon?: string;
  handleClick?: MouseEventHandler<HTMLButtonElement>;
}

export interface OptionProps {
  title: string;
  value: string;
}

export interface CustomFilterProps {
  title: string;
  options: OptionProps[];
}

export interface PriceCustomFilterProps {
  title: string;          // The title of the filter
  minPrice: number;      // Minimum price for the range
  maxPrice: number;      // Maximum price for the range
}


export interface ShowMoreProps {
  currentLength: number;
  pageNumber: number;
  isNext: boolean;
}

export interface SearchManuFacturerProps {
  manufacturer: string;
  setManuFacturer: (manufacturer: string) => void;
}
