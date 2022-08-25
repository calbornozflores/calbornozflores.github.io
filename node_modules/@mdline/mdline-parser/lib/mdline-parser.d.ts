import { MdlineFormat } from "@mdline/types";
export declare function parseHeading(text: string): {
    title: string;
    beginDate: string;
    endDate?: string;
} | null;
export declare function parse(text: string): MdlineFormat;
