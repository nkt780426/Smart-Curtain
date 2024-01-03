import tw from 'tailwind-styled-components';

const Input = tw.input`rounded-lg border-transparent
flex-1 appearance-none border
border-gray-300 px-4 py-2 bg-white
text-gray-700 placeholder-gray-400 shadow-sm 
text-base focus:outline-none focus:ring-2
focus:ring-pink-500 focus:border-transparent
disabled:bg-gray-100 disabled:text-gray-500
`;

export default Input;
