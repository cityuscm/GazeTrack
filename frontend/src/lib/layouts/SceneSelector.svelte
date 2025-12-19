<script lang="ts">
	interface Props {
		env? : 'prod' | 'test'
	}
	
	import Button from '$lib/components/Button.svelte';
	import Backdrop from '$lib/components/decorations/Backdrop.svelte';
	import Header from '$lib/components/Header.svelte';
	import Heading from '$lib/components/Heading.svelte';
	import CoordsPreview from '$lib/components/CoordsPreview.svelte';
	import { onMount } from 'svelte';
	import { apiRoutes } from '$lib/connection.svelte';
	import type { Session } from '$lib/structs';

	const {env = 'test'} = $props();
	const testClients = ['127.0.0.1', '192.168.1.1']
	const testScenes = ['NDI Test', 'Scene 2']

	let clients: string[] = $state([]);
	let mask: boolean[] = $state([]);
	let scenes: string[] = $state([]);

	const selectedClients = $derived(clients.filter((_, index) => mask[index]));

	const launchSession = (scene: string) => {
		const payload: Session = {
			clients: selectedClients,
			scene: scene
		};
		console.log('Launching session:', payload);
		if (env === 'test') {
			console.log(`DRY RUN CLIENTS: ${clients}`)
			console.log(`DRY RUN SCENE: ${scene}`)
		} else {
			apiRoutes.session(payload);
		}
	};

	onMount(async () => {
		if (env === 'test') {
			clients = testClients;
			mask = Array.from({length: testClients.length}).fill(false) as boolean[]
			scenes = testScenes;
		} else {
			const clientData = await (await apiRoutes.client()).json();
			const sceneData = await (await apiRoutes.scene()).json();
			console.log(`Got clients: ${clientData}`)
			console.log(`Got scenes: ${sceneData}`)
			clients = clientData || [];
			scenes = sceneData || [];
		}
	})
</script>

<article class="parent-size">
	<Backdrop />
	<div class="parent-size flex flex-col gap-4 items-center">
		<Header />
		<div class="grid grid-cols-4 grid-rows-1 gap-8">
			<div class="col-span-1 row-span-1 flex flex-col gap-4">
				<Heading title="Clients" color="purple" />
				{#each clients as client, index}
				<Button name="Client {index + 1}" address={client} type="toggle" bind:selected={mask[index]} />
				{/each}
			</div>
			<div class="col-span-1 row-span-1 flex flex-col gap-4">
				<Heading title="Scenes" color="blue" />
				{#each scenes as scene, index}
				<Button name="Scene {index + 1}" address={scene} onclick={() => launchSession(scene)} />
				{/each}
			</div>
			<div class="col-span-2 row-span-1 flex flex-col justify-center items-center gap-2">
				<Heading title="Preview" color="green" />
				<CoordsPreview />
			</div>
		</div>
	</div>
</article>
