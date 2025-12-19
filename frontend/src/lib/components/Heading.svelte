<script module lang="ts">
	const bgClasses: Record<string, string> = {
		purple: 'bg-purple-300/25',
		blue: 'bg-blue-300/25',
		green: 'bg-green-300/25',
		yellow: 'bg-yellow-300/25',
		orange: 'bg-orange-300/25',
		pink: 'bg-pink-300/25'
	};
	const borderClasses: Record<string, string> = {
		purple: 'border-purple-300',
		blue: 'border-blue-300',
		green: 'border-green-300',
		yellow: 'border-yellow-300',
		orange: 'border-orange-300',
		pink: 'border-pink-300'
	};
	const lineClasses: Record<string, string> = {
		purple: 'bg-purple-300',
		blue: 'bg-blue-300',
		green: 'bg-green-300',
		yellow: 'bg-yellow-300',
		orange: 'bg-orange-300',
		pink: 'bg-pink-300'
	};
</script>

<script lang="ts">
	interface Props {
		title: string;
		color: string;
	}
	let { title, color }: Props = $props();

	const bgClass = bgClasses[color];
	const borderClass = borderClasses[color];
	const lineClass = lineClasses[color];
</script>

<div class="relative w-full mb-2">
	<div class="parent-size bg-black/50 rounded-r-md"></div>
	<div
		class=" {bgClass} {borderClass} w-full h-full rounded-r-md border-l-2 backdrop-blur-[2px] flex items-center gap-2 -translate-1"
	>
		<div class="w-1 h-full {lineClass} "></div>
		<span class="text-lg font-thin text-white p-1">{title}</span>
	</div>
</div>
