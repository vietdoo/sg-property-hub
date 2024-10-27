import React from 'react';
import FeatureList from '@components/product/feature-list';
import { HouseProps } from "@types";

export function ProductDetails({ product }: { product: HouseProps }) {
 
    const featureData = [
        { label: 'Loại hình', value: product.property_type },
        { label: 'Nguồn', value: product.site },

        { label: 'Diện tích (m2)', value: product.attr_area },
        { label: 'Chiều ngang (m)', value: product.attr_width ?? 'N/A' },
        { label: 'Chiều dài (m)', value: product.attr_length ?? 'N/A' },
        { label: 'Số tầng', value: product.attr_floor ?? 'N/A' },

        { label: 'Số phòng', value: product.attr_total_room ?? 'N/A' },
        { label: 'Số PN', value: product.attr_bathroom ?? 'N/A' },
        { label: 'Số WC', value: product.attr_bedroom ?? 'N/A' },

        { label: 'Hướng', value: product.attr_direction },
        { label: 'Tình trạng', value: product.attr_condition },
        { label: 'Chứng chỉ', value: product.attr_certificate },
        { label: 'Đặc điểm', value: product.attr_feature },
        { label: 'Loại hình chi tiết', value: product.attr_type_detail },

        { label: 'Thành phố', value: product.location_city },
        { label: 'Quận', value: product.location_dist },
        { label: 'Phường', value: product.location_ward},
        { label: 'Đường', value: product.location_street },
        { label: 'Địa chỉ', value: product.location_address },

        { label: 'Vĩ độ', value: product.location_lat },
        { label: 'Kinh độ', value: product.location_long },

        { label: 'Môi giới', value: product.agent_name },
        { label: 'Email', value: product.agent_email },
        { label: 'Số điện thoại', value: product.agent_phone_number },
        { label: 'Địa chỉ', value: product.agent_address },
        { label: 'Loại môi giới', value: product.agent_agent_type },
        { label: 'Hồ sơ môi giới', value: product.agent_profile },
        { label: 'Hồ sơ dự án', value: product.project_profile },
        { label: 'Tên dự án', value: product.project_name },
    ];

    return (
        <div className="p-6">
            <FeatureList features={featureData} />
        </div>
    );
};


