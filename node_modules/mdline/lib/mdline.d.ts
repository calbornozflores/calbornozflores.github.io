import { MdlineParser, MdlineFormatter } from "@mdline/types";
export declare function processText(input: string, options: {
    parser: MdlineParser;
    formatter: MdlineFormatter;
}): Promise<string>;
