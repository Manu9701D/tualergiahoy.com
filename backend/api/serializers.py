# api/serializers.py
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100, trim_whitespace=True)
    apellidos = serializers.CharField(max_length=100, trim_whitespace=True)
    fecha_nacimiento = serializers.DateField()
    ciudad = serializers.CharField(max_length=100, trim_whitespace=True)
    alergias = serializers.ListField(
        child=serializers.CharField(max_length=100, trim_whitespace=True),
        allow_empty=True,
        default=list,
    )
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    nivel_sensibilidad = serializers.ChoiceField(
        choices=["bajo", "medio", "alto"], required=False, default="medio"
    )

    def validate(self, attrs):
        # Limpiamos posibles problemas de encoding
        for key in ["nombre", "apellidos", "ciudad"]:
            if key in attrs and isinstance(attrs[key], str):
                attrs[key] = (
                    attrs[key].replace("Ã©", "é").replace("Ã¡", "á").replace("Ã­", "í")
                )
        return attrs
