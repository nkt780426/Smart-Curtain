/** @format */

'use client';

import axios from 'axios';

axios.defaults.baseURL =
	process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

axios.interceptors.request.use((req) => {
	if (localStorage.getItem('accessToken')) {
		req.headers.authorization = `Bearer ${localStorage.getItem('accessToken')}`;
	}
	return req;
});

export const logIn = (params: { username: string; password: string }) =>
	axios.post('/login', params);

export const registerApi = (params: { username: string; password: string }) =>
	axios.post('/register', params);

export const getStatusApi = () => axios.get('/status');

export const changeAutoMode = (params: { status: boolean; percent: number }) =>
	axios.post('/auto', params);

export const postDailyAlarm = (params: {
	percent: number;
	hours: number;
	minutes: number;
}) => axios.post('/daily_alarm', params);

export const postOnceAlarm = (params: {
	percent: number;
	specify_time: string;
}) => axios.post('/once_alarm', params);

