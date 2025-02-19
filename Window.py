from tkinter import*

def printer(event):
    print("Elit-02")


def otvet(event):
    a = ent.get()
    if a == "5":
        print("a=", a)
    elif a == "n":
        print(a)
    elif a == "":
        print("this string is empty")
    else:
        print("p")


root = Tk()


root.minsize(width=200, height=300)
but = Button(root,
             text='Krutoi text',
             width=15, height=2,
             bg='black', fg='white')
but2 = Button(root,
             text='Print ent',
             width=15, height=2,
             bg='black', fg='white')
lab = Label(text='Text \n input', font='Arial 18')
ent = Entry(root,
            width=15, bd=3)


but.bind("<Button-1>", printer)
but2.bind('<Button-1>', otvet)

but2.pack()
lab.pack()
ent.pack()
but.pack()
root.mainloop()