const { createApp, reactive, ref, onMounted } = Vue;
const deepClone = obj => JSON.parse(JSON.stringify(obj));
createApp({
    setup() {
        const defaultC = {  appKey: '', useFrontendCdn: false };
        const config = reactive(deepClone(defaultC));
        const errors = reactive({});
        const hasApi = ref(false);
        const loading = ref(false);
        const fileInput = ref(null);

        const baseRules = {  appKey: 'required' };
        const baseRulesMessages = {
            required: "Field is required",
        }

        function validateAll() {
            const data = { ...config };
            const v = new Validator(data, baseRules, baseRulesMessages);
            if (v.fails()) {
                Object.assign(errors, v.errors.all());
                return false;
            }
            Object.keys(errors).forEach(k => delete errors[k]);
            return true;
        }

        function validateField(field) {
            const val = {};
            val[field] = get(config, field);
            const rul = {};
            rul[field] = getRule(field);
            const v = new Validator(val, rul, baseRulesMessages);
            if (v.fails()) errors[field] = v.errors.get(field);
            else delete errors[field];
        }

        function getRule(field) {
            return baseRules[field] || '';
        }

        function inputCls(field) {
            return [
                'w-full px-3 py-2 bg-input border rounded-md  ring-green-custom text-white',
                errors[field] ? 'border-red-500' : 'border-input'
            ].join(' ');
        }

        function get(obj, path) { return path.split('.').reduce((o, k) => o?.[k], obj); }
     

        function loadFile(e) {
            const file = e.target.files[0];
            if (!file || file.type !== 'application/json') return alert('Invalid json file. Please select a valid JSON file.');
            const r = new FileReader();
            r.onload = ev => {
                try {
                    Object.assign(config, deepClone(defaultC), JSON.parse(ev.target.result));
                    Object.keys(errors).forEach(k => delete errors[k]);
                } catch (err) { alert('Error parsing JSON: ' + err.message); }
            };
            r.readAsText(file);
            e.target.value = '';
        }

        function scrollToFirstError() {
            setTimeout(() => {
                const element = document.querySelector('.error-msg');
                    if (element) {
                        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        element.focus();
                    }
            }, 300);
        }

        function downloadJSON() {
            if (!validateAll()) {
                alert('There are validation errors. Please fix them before saving.')
                scrollToFirstError()
                return
            };
            const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
            const downloadAnchor = document.createElement('a');
            downloadAnchor.href = URL.createObjectURL(blob);
            downloadAnchor.download = 'config.json';
            downloadAnchor.click();
            URL.revokeObjectURL(downloadAnchor.href);
        }
        onMounted(() => {
            lucide.createIcons();
        });

        return {
            config, errors, loading, fileInput, hasApi,
            loadFile, downloadJSON,
            validateField, inputCls
        };
    }
}).mount('#app');