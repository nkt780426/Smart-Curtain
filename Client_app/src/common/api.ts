/** @format */

import axios from 'axios';

axios.defaults.baseURL =
	process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

axios.interceptors.request.use((req) => {
	if (localStorage.getItem('accessToken')) {
		req.headers.authorization = localStorage.getItem('accessToken');
	}
	return req;
});

export const logIn = (params: { username: string; password: string }) =>
	axios.post('/login', params);

export const registerApi = (params: { username: string; password: string }) =>
	axios.post('/register', params);
