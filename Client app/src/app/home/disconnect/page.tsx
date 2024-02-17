'use client'

import { PinkButton } from "@/components/base/Button";
import { useRouter } from "next/navigation";

const Disconnect = () => {
  const router = useRouter()

  return <div className="container md:max-w-[80vw] m-auto px-5 mt-4 justify-center grid">
    <div className="m-auto my-2">ESP32 disconnect to broker</div>
    {/* <PinkButton className='m-auto' onClick={() => router.push('/home')}>Back to home</PinkButton> */}
  </div>;
};
export default Disconnect;
