"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Truck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/store/auth";

const registerSchema = z
  .object({
    first_name: z.string().min(1, "Prenom requis"),
    last_name: z.string().min(1, "Nom requis"),
    email: z.string().email("Email invalide"),
    password: z.string().min(8, "8 caracteres minimum"),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Les mots de passe ne correspondent pas",
    path: ["confirm_password"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const registerUser = useAuthStore((s) => s.register);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setError(null);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
      });
      router.push("/login?registered=true");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur lors de l'inscription");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 sm:p-12 bg-bg dark:bg-bg-dark">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-10">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Truck className="w-4 h-4 text-white" />
          </div>
          <span className="font-display font-bold text-lg text-primary dark:text-white">
            MMS<span className="text-accent">Express</span>
          </span>
        </div>

        <h1 className="font-display font-bold text-2xl sm:text-3xl text-gray-900 dark:text-white mb-2">
          Creer un compte
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          Rejoignez MMS Express pour gerer vos livraisons
        </p>

        {error && (
          <div className="bg-error-light dark:bg-error/10 text-error text-sm font-medium px-4 py-3 rounded-[10px] mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Prenom"
              placeholder="Jean"
              error={errors.first_name?.message}
              {...register("first_name")}
            />
            <Input
              label="Nom"
              placeholder="Dupont"
              error={errors.last_name?.message}
              {...register("last_name")}
            />
          </div>

          <Input
            label="Email"
            type="email"
            placeholder="vous@entreprise.com"
            error={errors.email?.message}
            {...register("email")}
          />

          <Input
            label="Mot de passe"
            type="password"
            placeholder="8 caracteres minimum"
            error={errors.password?.message}
            {...register("password")}
          />

          <Input
            label="Confirmer le mot de passe"
            type="password"
            placeholder="Repetez votre mot de passe"
            error={errors.confirm_password?.message}
            {...register("confirm_password")}
          />

          <Button
            type="submit"
            isLoading={isSubmitting}
            className="w-full"
            size="lg"
          >
            Creer mon compte
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-8">
          Deja un compte ?{" "}
          <Link
            href="/login"
            className="font-medium text-accent hover:text-accent-dark transition-colors"
          >
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}
