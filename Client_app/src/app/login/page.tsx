'use client';

import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { useRouter } from 'next/navigation';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import clsx from 'clsx';
import Input from '@/components/base/Input';
import { ErrorText } from '@/components/base/ErrorText';
import { PinkButton } from '@/components/base/Button';
import { API } from '@/common/api';

const LoginSchema = yup.object().shape({
  username: yup
    .string()
    .required('Username is required'),
  password: yup
    .string()
    .required('Password is required')
});

export default function Login() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(LoginSchema) });

  const onSubmit = (data: any) => {
    console.log(data)
    API.post('/login', data)
      .then(res => {
        console.log(res)
      })
      .catch(err => {
        console.log(err)
      })
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-white sm:bg-gradient-to-tr from-purple-300 to-blue-300">
      <div className="grid p-5 md:p-10 justify-items-center w-auto m-auto bg-white rounded-2xl">
        <div className="text-center text-[20px] font-bold mb-5 text-black max-w-[400px] min-w-[80vw] md:min-w-[400px]">
          Login
          <div className="text-[14px] font-normal">
            Welcome back. Nice to see you again
          </div>
        </div>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="w-full max-w-[500px] grid"
        >
          <Input
            className={clsx('w-full', errors?.username ? 'mb-0' : 'mb-2')}
            placeholder="Username"
            {...register('username')}
          />
          <ErrorText>{errors.username?.message}</ErrorText>

          <Input
            className={clsx('w-full', errors?.password ? 'mb-0' : 'mb-2')}
            placeholder="Password"
            {...register('password')}
          />
          <ErrorText>{errors.password?.message}</ErrorText>
          {/* <div
            className="text-gray-800 italic mt-2 mb-4 text-right underline text-[15px] w-fit justify-self-end"
          >
            Forget your password?
          </div> */}
          <PinkButton
            className={clsx('w-full uppercase')}
            onClick={handleSubmit(onSubmit)}
          >
            Log in
          </PinkButton>
        </form>
      </div>
    </main>
  );
}
