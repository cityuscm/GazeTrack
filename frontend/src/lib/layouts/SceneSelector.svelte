<script lang="ts">
	interface Props {
		env?: 'prod' | 'test';
	}

	import Button from '$lib/components/Button.svelte';
	import Backdrop from '$lib/components/decorations/Backdrop.svelte';
	import Header from '$lib/components/Header.svelte';
	import Heading from '$lib/components/Heading.svelte';
	import CoordsPreview from '$lib/components/CoordsPreview.svelte';
	import { onMount } from 'svelte';
	import { apiRoutes } from '$lib/connection.svelte';
	import type { Session } from '$lib/structs';

	const { env = 'test' }: Props = $props();
	const testClients = ['127.0.0.1', '192.168.1.1'];
	const testScenes = ['NDI Test', 'Scene 2'];

	let clients: string[] = $state([]);
	let mask: boolean[] = $state([]);
	let scenes: string[] = $state([]);
	let loading: boolean = $state(true);
	let error: string | null = $state(null);
	const maxRetries: number = 3;

	const selectedClients = $derived(clients.filter((_, index) => mask[index]));

	const launchSession = async (scene: string) => {
		try {
			const payload: Session = {
				clients: selectedClients,
				scene: scene
			};
			console.log('Launching session:', payload);
			if (env === 'test') {
				console.log(`DRY RUN CLIENTS: ${clients}`);
				console.log(`DRY RUN SCENE: ${scene}`);
			} else {
				const response = await apiRoutes.session(payload);
				if (!response.ok) {
					throw new Error(`Session creation failed: ${response.status} ${response.statusText}`);
				}
				console.log('Session created successfully');
			}
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
			console.error('Failed to launch session:', errorMessage);
			error = `Failed to launch session: ${errorMessage}`;
			// Auto-clear error after 5 seconds
			setTimeout(() => {
				error = null;
			}, 5000);
		}
	};

	const fetchData = async (retryAttempt: number = 0): Promise<void> => {
		try {
			loading = true;
			error = null;

			if (env === 'test') {
				// Simulate network delay for test mode
				await new Promise((resolve) => setTimeout(resolve, 500));
				clients = testClients;
				mask = Array.from({ length: testClients.length }).fill(false) as boolean[];
				scenes = testScenes;
			} else {
				// Fetch clients with error handling
				let clientData: string[] = [];
				try {
					const clientResponse = await apiRoutes.client();
					if (!clientResponse.ok) {
						throw new Error(
							`Client API failed: ${clientResponse.status} ${clientResponse.statusText}`
						);
					}
					clientData = Object.keys(await clientResponse.json());
				} catch (err) {
					console.error('Failed to fetch clients:', err);
					throw new Error(
						`Failed to fetch clients: ${err instanceof Error ? err.message : 'Unknown error'}`
					);
				}

				// Fetch scenes with error handling
				let sceneData: string[] = [];
				try {
					const sceneResponse = await apiRoutes.scene();
					if (!sceneResponse.ok) {
						throw new Error(
							`Scene API failed: ${sceneResponse.status} ${sceneResponse.statusText}`
						);
					}
					sceneData = await sceneResponse.json();
				} catch (err) {
					console.error('Failed to fetch scenes:', err);
					throw new Error(
						`Failed to fetch scenes: ${err instanceof Error ? err.message : 'Unknown error'}`
					);
				}

				console.log(`Got clients: ${clientData}`);
				console.log(`Got scenes: ${sceneData}`);

				clients = clientData || [];
				scenes = sceneData || [];
				// Fix mask array to match actual client count
				mask = Array.from({ length: clients.length }).fill(false) as boolean[];
			}

			// Reset successful - no need to track retry count
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
			console.error('Data fetch error:', errorMessage);

			if (retryAttempt < maxRetries) {
				console.log(`Retrying data fetch (${retryAttempt + 1}/${maxRetries})...`);
				// Exponential backoff: 1s, 2s, 4s
				const delay = Math.pow(2, retryAttempt) * 1000;
				await new Promise((resolve) => setTimeout(resolve, delay));
				return fetchData(retryAttempt + 1);
			} else {
				error = `Failed to load data after ${maxRetries} attempts: ${errorMessage}`;
				clients = [];
				scenes = [];
				mask = [];
			}
		} finally {
			loading = false;
		}
	};

	onMount(async () => {
		await fetchData();
	});
</script>

<article class="parent-size">
	<Backdrop />
	<div class="parent-size flex flex-col gap-4 items-center">
		<Header />

		<!-- Error Display -->
		{#if error}
			<div
				class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-md"
			>
				<span class="block sm:inline">{error}</span>
				<button class="absolute top-0 bottom-0 right-0 px-4 py-3" onclick={() => (error = null)}>
					×
				</button>
			</div>
		{/if}

		<!-- Loading State -->
		{#if loading}
			<div class="flex items-center justify-center h-32">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
				<span class="ml-2 text-gray-600">Loading...</span>
			</div>
		{:else}
			<div class="grid grid-cols-4 grid-rows-1 gap-8">
				<div class="col-span-1 row-span-1 flex flex-col gap-4">
					<Heading title="Clients" color="purple" />
					{#if clients.length === 0}
						<div class="text-gray-500 text-center py-4">No clients available</div>
					{:else}
						{#each clients as client, index (index)}
							<Button
								name="Client {index + 1}"
								address={client}
								type="toggle"
								bind:selected={mask[index]}
							/>
						{/each}
					{/if}
				</div>

				<div class="col-span-1 row-span-1 flex flex-col gap-4">
					<Heading title="Scenes" color="blue" />
					{#if scenes.length === 0}
						<div class="text-gray-500 text-center py-4">No scenes available</div>
					{:else}
						{#each scenes as scene, index (index)}
							<Button
								name="Scene {index + 1}"
								address={scene}
								onclick={() => launchSession(scene)}
								disabled={selectedClients.length === 0}
							/>
						{/each}
					{/if}
				</div>

				<div class="col-span-2 row-span-1 flex flex-col justify-center items-center gap-2">
					<Heading title="Preview" color="green" />
					<CoordsPreview />

					<!-- Selection Summary -->
					{#if selectedClients.length > 0}
						<div class="text-sm text-gray-600 text-center">
							{selectedClients.length} client{selectedClients.length === 1 ? '' : 's'} selected
						</div>
					{:else}
						<div class="text-sm text-gray-400 text-center">Select clients to enable scenes</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</article>
