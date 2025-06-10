<template>
    <h1>Intervenants</h1>
    <p>Cette page est en cours de développement.</p>
    <p>Pour l'instant, vous pouvez consulter la liste des intervenants.</p>
    <p>Plus d'informations à venir !</p>
</template>

<script setup>

// Récupérer la liste des intervenants depuis l'API
import { ref, onMounted } from 'vue';
import { fetchIntervenants } from '@/services/intervenants';

const intervenants = ref([]);
onMounted(async () => {
    try {
        intervenants.value = await fetchIntervenants();
    } catch (error) {
        console.error('Erreur lors de la récupération des intervenants:', error);
    }
});

</script>