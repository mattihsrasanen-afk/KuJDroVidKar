echo "--- Säädetään palomuuria (portti 9000) ---"
if command -v ufw > /dev/null; then
    ufw allow 9000/tcp
    echo "UFW portti 9000 avattu."
else
    echo "UFW ei ole asennettu. Varmista käsin, että portti 9000 on auki palomuuristasi."
fi
