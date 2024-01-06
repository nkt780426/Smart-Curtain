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
import { registerApi } from '@/common/api';
import Link from 'next/link';

const RegisterSchema = yup.object().shape({
  username: yup
    .string()
    .required('Username is required'),
  password: yup
    .string()
    .required('Password is required'),
  confirmPassword: yup
    .string()
    .required('Confirm password is required'),
});

export default function Register() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm({ resolver: yupResolver(RegisterSchema) });

  const onSubmit = (data: any) => {
    if (data.password !== data.confirmPassword) {
      setError('confirmPassword', { message: 'Confirm password is not match' })
      return
    }
    registerApi(data)
      .then(res => {
        toast.success('Register successfully')
        router.push('/login')
      })
      .catch(err => {
        toast.error(err.response.data.error || 'Try again')
      })
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-white sm:bg-gradient-to-tr from-purple-300 to-blue-300">
      <div className="grid p-5 md:p-10 justify-items-center w-auto m-auto bg-white rounded-2xl">
        <div className="text-center text-[20px] font-bold mb-5 text-black max-w-[400px] min-w-[80vw] md:min-w-[400px]">
          Register
          <div className="text-[14px] font-normal">
            Create your account to continue
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
            type='password'
          />
          <ErrorText>{errors.password?.message}</ErrorText>

          <Input
            className={clsx('w-full', errors?.confirmPassword ? 'mb-0' : 'mb-2')}
            placeholder="Confirm your password"
            {...register('confirmPassword')}
            type='password'
          />
          <ErrorText>{errors.confirmPassword?.message}</ErrorText>

          <PinkButton
            className={clsx('w-full uppercase')}
            onClick={handleSubmit(onSubmit)}
          >
            Register
          </PinkButton>
          <Link href='/login' className='text-gray-800 underline italic text-sm w-fit mx-auto mt-1'>Already have an account? Log in</Link>
        </form>
      </div>
    </main>
  );
}
