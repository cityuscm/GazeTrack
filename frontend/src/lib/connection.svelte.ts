import type { Session } from '$lib/structs';

class ApiError extends Error {
	constructor(
		public message: string,
		public status?: number,
		public statusText?: string
	) {
		super(message);
		this.name = 'ApiError';
	}
}

interface RequestOptions extends RequestInit {
	timeout?: number;
	retries?: number;
	retryDelay?: number;
}

const DEFAULT_TIMEOUT = 10000; // 10 seconds
const DEFAULT_RETRIES = 3;
const DEFAULT_RETRY_DELAY = 1000; // 1 second

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

const createTimeoutController = (timeoutMs: number): AbortController => {
	const controller = new AbortController();
	setTimeout(() => controller.abort(), timeoutMs);
	return controller;
};

const makeRequestWithRetry = async (
	url: string,
	options: RequestOptions = {}
): Promise<Response> => {
	const {
		timeout = DEFAULT_TIMEOUT,
		retries = DEFAULT_RETRIES,
		retryDelay = DEFAULT_RETRY_DELAY,
		...fetchOptions
	} = options;

	let lastError: Error;

	for (let attempt = 0; attempt <= retries; attempt++) {
		try {
			const controller = createTimeoutController(timeout);

			const response = await fetch(url, {
				...fetchOptions,
				signal: controller.signal,
				headers: {
					'Content-Type': 'application/json',
					...fetchOptions.headers
				}
			});

			if (!response.ok) {
				throw new ApiError(
					`HTTP ${response.status}: ${response.statusText}`,
					response.status,
					response.statusText
				);
			}

			return response;
		} catch (error) {
			lastError = error as Error;

			// Don't retry on certain error types
			if (error instanceof ApiError && error.status && error.status >= 400 && error.status < 500) {
				throw error;
			}

			// Don't retry on abort (timeout)
			if (error instanceof Error && error.name === 'AbortError') {
				throw new ApiError('Request timeout', undefined, 'Timeout');
			}

			if (attempt < retries) {
				// Exponential backoff with jitter
				const delay = retryDelay * Math.pow(2, attempt) + Math.random() * 1000;
				await sleep(delay);
			}
		}
	}

	throw lastError!;
};

export const apiRoutes = {
	client: (options?: RequestOptions) =>
		makeRequestWithRetry('/api/clients', { ...options, method: 'GET' }),

	scene: (options?: RequestOptions) =>
		makeRequestWithRetry('/api/scenes', { ...options, method: 'GET' }),

	status: (options?: RequestOptions) =>
		makeRequestWithRetry('/api/status', { ...options, method: 'GET' }),

	session: (session: Session, options?: RequestOptions) =>
		makeRequestWithRetry('/api/session', {
			...options,
			method: 'POST',
			body: JSON.stringify(session)
		}),

	control: (start: boolean, options?: RequestOptions) =>
		makeRequestWithRetry(`/api/control?start=${start}`, {
			...options,
			method: 'POST'
		})
};

// Utility functions for common patterns
export const withErrorHandling = async <T>(
	apiCall: () => Promise<Response>,
	errorHandler?: (error: Error) => void
): Promise<T | null> => {
	try {
		const response = await apiCall();
		return (await response.json()) as T;
	} catch (error) {
		const err = error as Error;
		console.error('API call failed:', err);
		if (errorHandler) {
			errorHandler(err);
		}
		return null;
	}
};

export const withTimeout = async <T>(
	apiCall: () => Promise<T>,
	timeoutMs: number = DEFAULT_TIMEOUT
): Promise<T> => {
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

	try {
		const result = await apiCall();
		clearTimeout(timeoutId);
		return result;
	} catch (error) {
		clearTimeout(timeoutId);
		if (error instanceof Error && error.name === 'AbortError') {
			throw new ApiError('Operation timeout', undefined, 'Timeout');
		}
		throw error;
	}
};
