#!/bin/bash
if [ $# -eq 0 ]; then # Se nenhum argumento foi fornecido
	echo "Faltou o argumento, animal"
	exit 1
elif [ $# -eq 1 ]; then # Se passou apenas a mensagem
	git add .
	git commit -m "$1"
	git push
elif [ $# -eq 2 ]; then # Se passou msg e path
	git add $1
	git commit -m "$2"
	git push 
fi
