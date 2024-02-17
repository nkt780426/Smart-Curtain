import tw from "tailwind-styled-components";

const Button = tw.button`py-2 px-4 bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500 focus:ring-offset-indigo-200 text-white w-full transition ease-in duration-200 text-center text-base font-semibold shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2  rounded-lg`;

export default Button;

export const PinkButton = tw.button`
  rounded-lg
  bg-pink-500  
  hover:bg-pink-600
  text-white
  w-36
  py-2   
  px-4
`;

export const WhitePinkButton = tw.button`
  rounded-lg
  bg-white
  border
  border-pink-500
  hover:bg-gray-200
  text-pink-500
  w-36
  py-2
  px-4
`;
